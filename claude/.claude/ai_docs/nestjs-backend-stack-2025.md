# NestJS Backend Stack Best Practices (2025)

This document captures current best practices for building NestJS backends with ts-rest and Drizzle ORM, gathered January 2025.

## ts-rest: Contract-First API Development

### Overview
ts-rest provides end-to-end type safety for REST APIs without code generation. It enables defining API contracts that work seamlessly across client and server.

**Key Benefits:**
- End-to-end type safety
- RPC-like client interface
- Zero code generation required
- Zod schema support for runtime validation
- OpenAPI integration (optional)

### Installation

```bash
pnpm add @ts-rest/core @ts-rest/nest zod
```

### Defining Contracts

Contracts are the single source of truth, typically placed in a shared library:

```typescript
// libs/shared/api-contracts/src/lib/contracts/posts.contract.ts
import { initContract } from '@ts-rest/core';
import { z } from 'zod';

const c = initContract();

// Define Zod schemas (reusable for validation)
export const PostSchema = z.object({
  id: z.string().uuid(),
  title: z.string().min(1).max(200),
  content: z.string(),
  authorId: z.string().uuid(),
  createdAt: z.date(),
});

export const CreatePostSchema = PostSchema.omit({ id: true, createdAt: true });

export type Post = z.infer<typeof PostSchema>;
export type CreatePost = z.infer<typeof CreatePostSchema>;

// Define the contract
export const postsContract = c.router({
  getPosts: {
    method: 'GET',
    path: '/posts',
    query: z.object({
      skip: z.number().optional(),
      take: z.number().optional(),
    }),
    responses: {
      200: c.type<Post[]>(),
    },
  },
  getPost: {
    method: 'GET',
    path: '/posts/:id',
    pathParams: z.object({
      id: z.string().uuid(),
    }),
    responses: {
      200: c.type<Post>(),
      404: c.type<{ message: string }>(),
    },
  },
  createPost: {
    method: 'POST',
    path: '/posts',
    body: CreatePostSchema,
    responses: {
      201: c.type<Post>(),
      400: c.type<{ message: string }>(),
    },
  },
});
```

### NestJS Server Implementation

```typescript
// apps/api/src/posts/posts.controller.ts
import { Controller } from '@nestjs/common';
import { TsRestHandler, tsRestHandler } from '@ts-rest/nest';
import { postsContract } from '@myworkspace/api-contracts';
import { PostsService } from './posts.service';

@Controller()
export class PostsController {
  constructor(private readonly postsService: PostsService) {}

  @TsRestHandler(postsContract)
  async handler() {
    return tsRestHandler(postsContract, {
      getPosts: async ({ query }) => {
        const posts = await this.postsService.findAll(query);
        return { status: 200, body: posts };
      },
      getPost: async ({ params }) => {
        const post = await this.postsService.findOne(params.id);
        if (!post) {
          return { status: 404, body: { message: 'Post not found' } };
        }
        return { status: 200, body: post };
      },
      createPost: async ({ body }) => {
        const post = await this.postsService.create(body);
        return { status: 201, body: post };
      },
    });
  }
}
```

### Angular Client Usage

```typescript
// libs/posts/data-access/src/lib/posts.service.ts
import { Injectable, inject } from '@angular/core';
import { initClient } from '@ts-rest/core';
import { postsContract } from '@myworkspace/api-contracts';

@Injectable({ providedIn: 'root' })
export class PostsDataService {
  private client = initClient(postsContract, {
    baseUrl: '/api',
    baseHeaders: {},
  });

  async getPosts(skip = 0, take = 10) {
    const result = await this.client.getPosts({ query: { skip, take } });
    if (result.status === 200) {
      return result.body;
    }
    throw new Error('Failed to fetch posts');
  }

  async createPost(data: CreatePost) {
    const result = await this.client.createPost({ body: data });
    if (result.status === 201) {
      return result.body;
    }
    throw new Error('Failed to create post');
  }
}
```

---

## Drizzle ORM: NestJS Integration

### Overview
Drizzle ORM is a TypeScript-first ORM that's lightweight, performant, and provides excellent type safety. It's considered the fastest ORM for NestJS in 2025.

**Key Benefits:**
- Compiles to minimal SQL overhead
- Strict TypeScript type inference
- SQL-like query syntax
- Robust migration system
- Works with PostgreSQL, MySQL, SQLite

### Installation Options

**Option 1: Manual Integration (Recommended for control)**
```bash
pnpm add drizzle-orm pg
pnpm add -D drizzle-kit @types/pg
```

**Option 2: Using @knaadh/nestjs-drizzle-pg**
```bash
pnpm add @knaadh/nestjs-drizzle-pg drizzle-orm pg
pnpm add -D drizzle-kit @types/pg
```

**Option 3: Using @sixaphone/nestjs-drizzle (includes repository pattern)**
```bash
pnpm add @sixaphone/nestjs-drizzle drizzle-orm pg
pnpm add -D drizzle-kit @types/pg
```

### Configuration

Create `drizzle.config.ts` in workspace root or api app:

```typescript
import { defineConfig } from 'drizzle-kit';

export default defineConfig({
  dialect: 'postgresql',
  schema: './libs/shared/db/src/schema/index.ts',
  out: './libs/shared/db/drizzle',
  dbCredentials: {
    url: process.env.DATABASE_URL!,
  },
});
```

### Schema Definition

```typescript
// libs/shared/db/src/schema/posts.schema.ts
import { pgTable, uuid, text, timestamp } from 'drizzle-orm/pg-core';
import { users } from './users.schema';

export const posts = pgTable('posts', {
  id: uuid('id').primaryKey().defaultRandom(),
  title: text('title').notNull(),
  content: text('content').notNull(),
  authorId: uuid('author_id')
    .notNull()
    .references(() => users.id),
  createdAt: timestamp('created_at').defaultNow().notNull(),
  updatedAt: timestamp('updated_at').defaultNow().notNull(),
});

// Type inference
export type Post = typeof posts.$inferSelect;
export type NewPost = typeof posts.$inferInsert;
```

### Manual NestJS Integration (Recommended)

**Drizzle Provider:**
```typescript
// apps/api/src/database/drizzle.provider.ts
import { Provider } from '@nestjs/common';
import { ConfigService } from '@nestjs/config';
import { drizzle } from 'drizzle-orm/node-postgres';
import { Pool } from 'pg';
import * as schema from '@myworkspace/db/schema';

export const DRIZZLE = Symbol('DRIZZLE');

export const DrizzleProvider: Provider = {
  provide: DRIZZLE,
  inject: [ConfigService],
  useFactory: async (configService: ConfigService) => {
    const pool = new Pool({
      connectionString: configService.get<string>('DATABASE_URL'),
    });
    return drizzle(pool, { schema });
  },
};
```

**Drizzle Module:**
```typescript
// apps/api/src/database/drizzle.module.ts
import { Global, Module } from '@nestjs/common';
import { DrizzleProvider, DRIZZLE } from './drizzle.provider';

@Global()
@Module({
  providers: [DrizzleProvider],
  exports: [DRIZZLE],
})
export class DrizzleModule {}
```

**Service Usage:**
```typescript
// apps/api/src/posts/posts.service.ts
import { Injectable, Inject } from '@nestjs/common';
import { eq } from 'drizzle-orm';
import { NodePgDatabase } from 'drizzle-orm/node-postgres';
import { DRIZZLE } from '../database/drizzle.provider';
import * as schema from '@myworkspace/db/schema';
import { posts, NewPost } from '@myworkspace/db/schema';

@Injectable()
export class PostsService {
  constructor(
    @Inject(DRIZZLE) private db: NodePgDatabase<typeof schema>,
  ) {}

  async findAll(options?: { skip?: number; take?: number }) {
    return this.db.query.posts.findMany({
      limit: options?.take ?? 10,
      offset: options?.skip ?? 0,
      with: { author: true },
    });
  }

  async findOne(id: string) {
    return this.db.query.posts.findFirst({
      where: eq(posts.id, id),
      with: { author: true },
    });
  }

  async create(data: NewPost) {
    const [post] = await this.db.insert(posts).values(data).returning();
    return post;
  }

  async update(id: string, data: Partial<NewPost>) {
    const [post] = await this.db
      .update(posts)
      .set({ ...data, updatedAt: new Date() })
      .where(eq(posts.id, id))
      .returning();
    return post;
  }

  async delete(id: string) {
    await this.db.delete(posts).where(eq(posts.id, id));
  }
}
```

### Migration Scripts

Add to `package.json`:
```json
{
  "scripts": {
    "db:generate": "drizzle-kit generate",
    "db:migrate": "drizzle-kit migrate",
    "db:push": "drizzle-kit push",
    "db:studio": "drizzle-kit studio"
  }
}
```

---

## Nx + NestJS Integration

### Creating a NestJS Application

```bash
nx g @nx/nest:application apps/api
```

### Creating NestJS Libraries

```bash
# Standard library
nx g @nx/nest:lib libs/api/feature-posts

# Buildable library
nx g @nx/nest:lib libs/api/feature-posts --buildable

# Publishable library
nx g @nx/nest:lib libs/api/feature-posts --publishable --importPath=@myworkspace/api-feature-posts
```

### Generating NestJS Components

```bash
# Module
nx g @nx/nest:module --project=api --name=posts

# Controller
nx g @nx/nest:controller --project=api --name=posts

# Service
nx g @nx/nest:service --project=api --name=posts

# Resource (module + controller + service + DTOs)
nx g @nx/nest:resource --project=api --name=posts
```

### VSCode Debugging

Nx automatically creates `.vscode/launch.json` with:
- Smart port allocation (starting from 9229)
- Source map support
- Multi-format support (.js, .mjs, .cjs)

---

## Recommended Monorepo Structure

```
libs/
  shared/
    api-contracts/      # ts-rest contracts + Zod schemas
      src/
        lib/
          contracts/
            index.ts
            posts.contract.ts
            users.contract.ts
          schemas/
            index.ts
            post.schema.ts
            user.schema.ts
    db/                 # Drizzle schemas + migrations
      src/
        schema/
          index.ts
          posts.schema.ts
          users.schema.ts
      drizzle/          # Generated migrations
    util/               # Pure functions, helpers
  <app>/
    data-access/        # Angular services consuming contracts

apps/
  api/                  # NestJS modular monolith
    src/
      database/
        drizzle.module.ts
        drizzle.provider.ts
      posts/
        posts.module.ts
        posts.controller.ts
        posts.service.ts
      app.module.ts
      main.ts
```

---

## Sources

- [ts-rest GitHub](https://github.com/ts-rest/ts-rest)
- [Trilon: NestJS & DrizzleORM](https://trilon.io/blog/nestjs-drizzleorm-a-great-match)
- [@knaadh/nestjs-drizzle](https://github.com/knaadh/nestjs-drizzle)
- [Drizzle ORM + NestJS Guide (dev.to)](https://dev.to/anooop102910/how-to-integrate-drizzle-orm-with-nest-js-gdc)
- [2025 NestJS + Drizzle Architecture](https://dev.to/xiunotes/2025-nestjs-react-19-drizzle-orm-turborepo-architecture-decision-record-3o1k)
- [Best ORM for NestJS 2025](https://dev.to/sasithwarnakafonseka/best-orm-for-nestjs-in-2025-drizzle-orm-vs-typeorm-vs-prisma-229c)

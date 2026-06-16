import { defineCollection, z } from 'astro:content';
import { glob } from 'astro/loaders';

// 解説記事（Explainers）。作品に紐づく読み物・教材。
const docs = defineCollection({
  loader: glob({ pattern: '**/*.md', base: './src/content/docs' }),
  schema: z.object({
    title: z.string(),
    description: z.string(),
    pubDate: z.coerce.date(),
    tags: z.array(z.string()).optional(),
    demo: z.string().optional(),        // 関連デモのURL（任意）
    demoLabel: z.string().optional(),
    series: z.string().optional(),      // トップで章立てするコースのキー
    order: z.number().optional(),       // コース内の読む順
    related: z.array(z.object({ title: z.string(), url: z.string() })).optional(), // 合わせて読みたいリンク（任意）
  }),
});

export const collections = { docs };

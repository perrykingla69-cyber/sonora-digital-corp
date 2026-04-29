import { NextResponse } from 'next/server';
import { scheduledPostsSeed } from '@/lib/mock-seed';

export async function POST(_: Request, context: { params: { id: string } }): Promise<NextResponse> {
  const post = scheduledPostsSeed.find((item) => item.id === context.params.id);
  if (!post) {
    return NextResponse.json({ error: 'Post no encontrado' }, { status: 404 });
  }

  post.status = 'approved';
  return NextResponse.json(post);
}

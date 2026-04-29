import { NextRequest, NextResponse } from 'next/server';
import { scheduledPostsSeed } from '@/lib/mock-seed';

export async function GET(request: NextRequest): Promise<NextResponse> {
  const dateParam = request.nextUrl.searchParams.get('date');
  if (!dateParam) {
    return NextResponse.json(scheduledPostsSeed);
  }

  const filtered = scheduledPostsSeed.filter((post) => post.scheduled_at.slice(0, 10) === dateParam);
  return NextResponse.json(filtered);
}

export async function POST(request: NextRequest): Promise<NextResponse> {
  const payload = await request.json();

  const newPost = {
    id: `post_${scheduledPostsSeed.length + 1}`,
    tenant_id: 'abe_music',
    status: 'pending_review',
    ...payload,
  };

  scheduledPostsSeed.push(newPost);
  return NextResponse.json(newPost, { status: 201 });
}

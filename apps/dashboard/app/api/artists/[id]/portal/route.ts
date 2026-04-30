import { NextResponse } from 'next/server';
import { artistPortalSeed } from '@/lib/mock-seed';

export async function GET(_: Request, context: { params: { id: string } }): Promise<NextResponse> {
  const artist = artistPortalSeed.find((item) => item.id === context.params.id);
  if (!artist) {
    return NextResponse.json({ error: 'Artista no encontrado' }, { status: 404 });
  }

  return NextResponse.json(artist);
}

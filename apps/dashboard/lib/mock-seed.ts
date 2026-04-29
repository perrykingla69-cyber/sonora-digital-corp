export interface ScheduledPost {
  id: string;
  tenant_id: string;
  artist: string;
  platform: 'tiktok' | 'instagram' | 'youtube_shorts' | 'youtube_main' | 'stories';
  content_type: 'hook' | 'behind_scenes' | 'performance' | 'lyric_video' | 'thumbnail';
  scheduled_at: string;
  status: 'pending_review' | 'approved' | 'published' | 'rejected';
  hook_text?: string;
  thumbnail_url?: string;
  metrics?: { views: number; likes: number; shares: number };
}

export interface ArtistPortal {
  id: string;
  name: string;
  avatar_url: string;
  streaming_numbers: { spotify_monthly: number; youtube_views: number; tiktok_followers: number };
  royalties: {
    current_month: number;
    previous_month: number;
    breakdown: Array<{ source: string; amount: number }>;
  };
  clone_status: { active: boolean; revenue_generated: number; uses_this_month: number };
  upcoming_content: ScheduledPost[];
  top_tracks: Array<{
    id: string;
    name: string;
    bpm: number;
    key: string;
    duration: string;
    energy_curve: number[];
    structure: Array<{ section: string; start: number; end: number }>;
  }>;
}

export const scheduledPostsSeed: ScheduledPost[] = [
  {
    id: 'post_1', tenant_id: 'abe_music', artist: 'Héctor Rubio', platform: 'tiktok', content_type: 'hook',
    scheduled_at: new Date().toISOString(), status: 'pending_review',
    hook_text: '¿Qué harías si hoy fuera la última vez que me ves?',
    thumbnail_url: 'https://picsum.photos/seed/hector1/640/360',
    metrics: { views: 21340, likes: 3450, shares: 270 },
  },
  {
    id: 'post_2', tenant_id: 'abe_music', artist: 'Héctor Rubio', platform: 'instagram', content_type: 'behind_scenes',
    scheduled_at: new Date(Date.now() + 86400000).toISOString(), status: 'approved',
    hook_text: 'Detrás de cámaras del nuevo corrido tumbado.',
    thumbnail_url: 'https://picsum.photos/seed/hector2/640/360',
  },
  {
    id: 'post_3', tenant_id: 'abe_music', artist: 'Christian Ortega', platform: 'youtube_shorts', content_type: 'performance',
    scheduled_at: new Date(Date.now() + 2 * 86400000).toISOString(), status: 'published',
    hook_text: 'Performance en vivo desde Hermosillo.',
    thumbnail_url: 'https://picsum.photos/seed/chris1/640/360',
    metrics: { views: 84200, likes: 7200, shares: 611 },
  },
];

export const artistPortalSeed: ArtistPortal[] = [
  {
    id: 'a1',
    name: 'Héctor Rubio',
    avatar_url: 'https://picsum.photos/seed/avatar-hector/200/200',
    streaming_numbers: { spotify_monthly: 1044718, youtube_views: 250000, tiktok_followers: 85000 },
    royalties: {
      current_month: 2450,
      previous_month: 1980,
      breakdown: [
        { source: 'Spotify', amount: 1850 },
        { source: 'YouTube', amount: 420 },
        { source: 'TikTok Sounds', amount: 180 },
      ],
    },
    clone_status: { active: true, revenue_generated: 1500, uses_this_month: 42 },
    upcoming_content: scheduledPostsSeed.filter((p) => p.artist === 'Héctor Rubio'),
    top_tracks: [
      {
        id: 't1', name: 'Necesito Verte', bpm: 110, key: 'C major', duration: '3:12',
        energy_curve: [0.2, 0.3, 0.4, 0.7, 0.9, 0.8, 0.5],
        structure: [
          { section: 'intro', start: 0, end: 12 },
          { section: 'verse', start: 12, end: 45 },
          { section: 'chorus', start: 45, end: 75 },
        ],
      },
    ],
  },
];

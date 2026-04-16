import { useAuth } from "@/_core/hooks/useAuth";
import { useLocation } from "wouter";
import { useState } from "react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { trpc } from "@/lib/trpc";
import { Heart, MessageCircle, Share2, Sparkles } from "lucide-react";

const DEMO_BAR_ID = 1;

export default function SocialFeed() {
  const { user, isAuthenticated } = useAuth();
  const [, setLocation] = useLocation();
  const [newPost, setNewPost] = useState("");
  const [likedPosts, setLikedPosts] = useState<number[]>([]);

  const getSocialFeed = trpc.conrado.getSocialFeed.useQuery({ barId: DEMO_BAR_ID, limit: 20 });
  const createPost = trpc.conrado.createSocialPost.useMutation();
  const likePost = trpc.conrado.likePost.useMutation();

  if (!isAuthenticated) {
    setLocation("/");
    return null;
  }

  const handleCreatePost = async () => {
    if (!newPost.trim()) return;
    try {
      await createPost.mutateAsync({
        barId: DEMO_BAR_ID,
        content: newPost,
        imageUrl: "https://via.placeholder.com/400x300",
      });
      setNewPost("");
      getSocialFeed.refetch();
    } catch (error) {
      console.error("Error creating post:", error);
    }
  };

  const handleLike = async (postId: number) => {
    if (likedPosts.includes(postId)) return;
    try {
      await likePost.mutateAsync({ postId, barId: DEMO_BAR_ID });
      setLikedPosts([...likedPosts, postId]);
      getSocialFeed.refetch();
    } catch (error) {
      console.error("Error liking post:", error);
    }
  };

  const demoPosts = [
    {
      id: 1,
      author: "Alejandro Zamora",
      role: "🎸 Artista Residente",
      content: "¡Qué noche increíble en Conrado! Gracias a todos los que disfrutaron la música.",
      image: "https://via.placeholder.com/400x300/6b21a8/ffffff?text=Alejandro+Zamora",
      likes: 156,
      comments: 24,
      tokens: 50,
      timestamp: "hace 2 horas",
    },
    {
      id: 2,
      author: "María García",
      role: "👑 VIP Gold",
      content: "El ambiente está de lujo esta noche. ¡Cheers! 🍺",
      image: "https://via.placeholder.com/400x300/ec4899/ffffff?text=Maria+Garcia",
      likes: 89,
      comments: 12,
      tokens: 30,
      timestamp: "hace 1 hora",
    },
    {
      id: 3,
      author: "Carlos López",
      role: "💎 VIP Diamante",
      content: "Conrado Botanero: donde la música, la comida y la compañía son perfectas.",
      image: "https://via.placeholder.com/400x300/f59e0b/ffffff?text=Carlos+Lopez",
      likes: 234,
      comments: 45,
      tokens: 75,
      timestamp: "hace 30 minutos",
    },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-purple-950 to-slate-950">
      {/* Header */}
      <div className="border-b border-purple-500/20 bg-slate-900/50 backdrop-blur sticky top-0 z-10">
        <div className="max-w-2xl mx-auto px-6 py-4">
          <h1 className="text-2xl font-bold text-white">📸 Feed Social</h1>
          <p className="text-purple-300 text-sm">Comparte, gana tokens, sube de nivel</p>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-2xl mx-auto px-6 py-8">
        {/* Create Post */}
        <Card className="bg-slate-900/50 border-purple-500/30 p-6 mb-8">
          <div className="flex gap-4 mb-4">
            <div className="w-12 h-12 rounded-full bg-gradient-to-br from-cyan-400 to-blue-400 flex items-center justify-center text-white font-bold">
              {user?.name?.[0] || "U"}
            </div>
            <div className="flex-1">
              <textarea
                value={newPost}
                onChange={(e) => setNewPost(e.target.value)}
                placeholder="¿Qué está pasando en Conrado?"
                className="w-full bg-slate-800/50 border border-purple-500/30 rounded-lg p-3 text-white placeholder-purple-400 focus:outline-none focus:border-purple-500 resize-none"
                rows={3}
              />
            </div>
          </div>
          <div className="flex justify-between items-center">
            <div className="text-sm text-purple-300">Ganarás tokens por engagement 🎉</div>
            <Button
              onClick={handleCreatePost}
              disabled={createPost.isPending || !newPost.trim()}
              className="bg-gradient-to-r from-cyan-500 to-blue-500 hover:from-cyan-600 hover:to-blue-600 text-white font-bold"
            >
              {createPost.isPending ? "Publicando..." : "Publicar"}
            </Button>
          </div>
        </Card>

        {/* Posts Feed */}
        <div className="space-y-6">
          {demoPosts.map((post) => (
            <Card key={post.id} className="bg-slate-900/50 border-purple-500/30 overflow-hidden hover:border-purple-500/60 transition-all">
              {/* Post Header */}
              <div className="p-6 border-b border-purple-500/20">
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center gap-3">
                    <div className="w-12 h-12 rounded-full bg-gradient-to-br from-pink-400 to-purple-400 flex items-center justify-center text-white font-bold">
                      {post.author[0]}
                    </div>
                    <div>
                      <p className="font-bold text-white">{post.author}</p>
                      <p className="text-sm text-purple-300">{post.role}</p>
                    </div>
                  </div>
                  <span className="text-xs text-purple-400">{post.timestamp}</span>
                </div>
              </div>

              {/* Post Content */}
              <div className="p-6 border-b border-purple-500/20">
                <p className="text-white mb-4">{post.content}</p>
                <img src={post.image} alt="Post" className="w-full rounded-lg mb-4 border border-purple-500/30" />
              </div>

              {/* Post Stats */}
              <div className="px-6 py-4 bg-slate-800/30 border-b border-purple-500/20 flex items-center justify-between text-sm">
                <div className="flex gap-4 text-purple-300">
                  <span>❤️ {post.likes} likes</span>
                  <span>💬 {post.comments} comentarios</span>
                </div>
                <div className="flex items-center gap-1 text-yellow-400 font-bold">
                  <Sparkles className="w-4 h-4" />
                  +{post.tokens} tokens
                </div>
              </div>

              {/* Post Actions */}
              <div className="p-6 flex gap-4">
                <Button
                  onClick={() => handleLike(post.id)}
                  disabled={likedPosts.includes(post.id)}
                  variant="outline"
                  className="flex-1 border-purple-500/30 text-purple-300 hover:bg-purple-500/10"
                >
                  <Heart className="w-4 h-4 mr-2" />
                  Me encanta
                </Button>
                <Button variant="outline" className="flex-1 border-purple-500/30 text-purple-300 hover:bg-purple-500/10">
                  <MessageCircle className="w-4 h-4 mr-2" />
                  Comentar
                </Button>
                <Button variant="outline" className="flex-1 border-purple-500/30 text-purple-300 hover:bg-purple-500/10">
                  <Share2 className="w-4 h-4 mr-2" />
                  Compartir
                </Button>
              </div>
            </Card>
          ))}
        </div>
      </div>
    </div>
  );
}

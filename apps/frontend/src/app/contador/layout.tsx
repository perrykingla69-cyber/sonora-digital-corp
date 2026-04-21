export const metadata = {
  title: 'Tablero Contador - HERMES',
  description: 'Gestión de obligaciones fiscales y compliance'
};

export default function ContadorLayout({
  children
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="min-h-screen bg-slate-900 text-white">
      <div className="max-w-7xl mx-auto px-4 py-8">
        {children}
      </div>
    </div>
  );
}

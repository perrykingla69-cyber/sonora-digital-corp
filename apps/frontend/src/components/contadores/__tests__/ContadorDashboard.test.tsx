import { describe, it, expect, beforeEach, vi } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import ContadorDashboard from '../ContadorDashboard';

// Mock fetch
global.fetch = vi.fn();

describe('ContadorDashboard', () => {
  beforeEach(() => {
    localStorage.setItem('token', 'test-token');
    vi.clearAllMocks();
  });

  it('renders dashboard on load', async () => {
    (global.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: async () => ({ user_stats: { level: 5, total_xp: 250 } })
    });
    (global.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: async () => ({ obligaciones: [], alertas: [] })
    });

    render(<ContadorDashboard />);

    await waitFor(() => {
      expect(screen.getByText('Tablero Contador')).toBeInTheDocument();
    });
  });

  it('displays obligaciones count', async () => {
    const mockObs = [
      { id: '1', nombre: 'ISR', vencimiento: '2026-05-31', régimen: 'RIF', completada: false },
      { id: '2', nombre: 'IVA', vencimiento: '2026-05-15', régimen: 'RIF', completada: true }
    ];

    (global.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: async () => ({ user_stats: {} })
    });
    (global.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: async () => ({ obligaciones: mockObs, alertas: [] })
    });

    render(<ContadorDashboard />);

    await waitFor(() => {
      expect(screen.getByText('2')).toBeInTheDocument(); // 2 obligaciones
    });
  });

  it('handles API errors gracefully', async () => {
    (global.fetch as any).mockRejectedValue(new Error('API Error'));

    render(<ContadorDashboard />);

    await waitFor(() => {
      expect(screen.getByText(/error/i)).toBeInTheDocument();
    });
  });
});

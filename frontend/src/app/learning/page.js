'use client';

import Link from 'next/link';
import { useRequireAuth } from '@/hooks/useRequireAuth';
import PageShell from '@/components/common/PageShell';

/**
 * Lightweight Learning / upskilling shell.
 *
 * Intentionally NOT a course marketplace and NOT personalized by a backend call.
 * It explains that the richest, personalized learning roadmap is produced by the
 * CV/JD analysis result, and offers static, evergreen upskilling tracks as a
 * starting point. No payment, no fake personalization claims.
 */

const TRACKS = [
  {
    icon: '📄',
    title: 'Resume / CV improvement',
    desc: 'Tighten your CV structure, quantify impact, and mirror the language of the roles you target.',
    href: '/dashboard',
    cta: 'Run a CV vs JD analysis',
  },
  {
    icon: '🎤',
    title: 'Interview practice',
    desc: 'Practice role-specific questions and review structured AI feedback on each answer.',
    href: '/applications',
    cta: 'Open an application',
  },
  {
    icon: '🛠',
    title: 'Technical skill gaps',
    desc: 'Close the missing-skill gaps surfaced by your analysis, one priority at a time.',
    href: '/dashboard',
    cta: 'See your skill gaps',
  },
  {
    icon: '📁',
    title: 'Portfolio / project evidence',
    desc: 'Capture projects and achievements in your Evidence Vault so AI materials cite real proof.',
    href: '/profile/evidence',
    cta: 'Build your evidence',
  },
];

export default function LearningPage() {
  const { isAuthChecking } = useRequireAuth();

  return (
    <PageShell isAuthChecking={isAuthChecking}>
      <h1 style={{ fontSize: 'var(--font-size-2xl)', fontWeight: 700, color: 'var(--color-text)', marginBottom: '0.5rem' }}>
        Learning Roadmap
      </h1>
      <p style={{ fontSize: 'var(--font-size-sm)', color: 'var(--color-text-secondary)', lineHeight: 1.6, marginBottom: '1.75rem', maxWidth: 640 }}>
        Upskilling tracks to strengthen your job readiness. Your most personalised roadmap is
        generated from a <strong>CV&nbsp;vs&nbsp;JD analysis</strong> — run one to see the exact
        skills to focus on next. The tracks below are good starting points for everyone.
      </p>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))', gap: '1rem', marginBottom: '2rem' }}>
        {TRACKS.map((track) => (
          <div
            key={track.title}
            style={{ border: '1px solid var(--color-border)', borderRadius: 'var(--radius-md)', padding: '1.25rem', background: 'var(--color-surface, #fff)', display: 'flex', flexDirection: 'column', gap: '0.5rem' }}
          >
            <div style={{ fontSize: '1.75rem' }}>{track.icon}</div>
            <div style={{ fontSize: 'var(--font-size-base)', fontWeight: 700, color: 'var(--color-text)' }}>{track.title}</div>
            <p style={{ fontSize: 'var(--font-size-sm)', color: 'var(--color-text-secondary)', lineHeight: 1.6, margin: 0, flex: 1 }}>
              {track.desc}
            </p>
            <Link href={track.href} style={{ fontSize: 'var(--font-size-sm)', fontWeight: 600, color: 'var(--color-primary)', textDecoration: 'none', display: 'inline-flex', alignItems: 'center', gap: 4 }}>
              {track.cta} →
            </Link>
          </div>
        ))}
      </div>

      <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.75rem', fontSize: 'var(--font-size-sm)' }}>
        <Link href="/dashboard" style={{ color: 'var(--color-primary)', textDecoration: 'none' }}>← Back to CV Analysis</Link>
        <span style={{ color: 'var(--color-text-muted)' }}>·</span>
        <Link href="/applications" style={{ color: 'var(--color-primary)', textDecoration: 'none' }}>Applications</Link>
        <span style={{ color: 'var(--color-text-muted)' }}>·</span>
        <Link href="/profile/evidence" style={{ color: 'var(--color-primary)', textDecoration: 'none' }}>Evidence Vault</Link>
        <span style={{ color: 'var(--color-text-muted)' }}>·</span>
        <Link href="/help" style={{ color: 'var(--color-primary)', textDecoration: 'none' }}>Help</Link>
      </div>
    </PageShell>
  );
}

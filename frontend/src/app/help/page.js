'use client';

import Link from 'next/link';
import { useRequireAuth } from '@/hooks/useRequireAuth';
import PageShell from '@/components/common/PageShell';

/**
 * Static guided Help / FAQ shell.
 *
 * Intentionally NOT a chatbot and NOT backed by an LLM call. It is a static,
 * curated walkthrough of the product flow so a new user (or a presenter) always
 * knows the next step. No backend dependency.
 */

const FAQS = [
  {
    q: 'What should I do first?',
    a: 'Start on CV Analysis. Upload your CV, paste a job description (JD), and run the analysis to get a fit score, matched/missing skills, and recommendations.',
  },
  {
    q: 'How do I analyze my CV against a job description?',
    a: 'Open CV Analysis, upload a PDF or DOCX CV, paste the JD, choose strictness and language, then start the analysis. The result appears with your fit score and skill gaps.',
  },
  {
    q: 'How do I create an application?',
    a: 'Go to Applications → New. Enter the company, role title, and the job description. Each application is a workspace for one target job.',
  },
  {
    q: 'How do I attach an analysis to an application?',
    a: 'Open the application and use “Attach analysis”. Pick a recent completed analysis from the list, or paste a Job ID from your Analysis History. Attaching unlocks interview practice, cover letter, and the readiness package.',
  },
  {
    q: 'How do I use interview practice?',
    a: 'From an application with an attached analysis, open Interview. Answer each AI-generated question and review the structured rubric feedback. Your answers are saved as history.',
  },
  {
    q: 'How do I generate a cover letter or readiness package?',
    a: 'From the application, open Cover Letter or Package and click Generate. Both require an attached analysis. The cover letter is fully editable and saveable.',
  },
  {
    q: 'What analytics events are tracked?',
    a: 'Only privacy-safe product events (e.g. page navigation, login, analysis started/completed, application created, generate/save actions). We never send CV text, JD text, interview answers, cover letter text, emails, tokens, or IDs.',
  },
  {
    q: 'Why should demo data be synthetic?',
    a: 'For presentations, use synthetic CVs/JDs and a demo account only. Never present real candidate data. This protects privacy and keeps the demo reproducible.',
  },
];

export default function HelpPage() {
  const { isAuthChecking } = useRequireAuth();

  return (
    <PageShell isAuthChecking={isAuthChecking}>
      <h1 style={{ fontSize: 'var(--font-size-2xl)', fontWeight: 700, color: 'var(--color-text)', marginBottom: '0.5rem' }}>
        Help &amp; Guide
      </h1>
      <p style={{ fontSize: 'var(--font-size-sm)', color: 'var(--color-text-secondary)', lineHeight: 1.6, marginBottom: '1.75rem', maxWidth: 640 }}>
        A quick guide to the AI CV Fit workflow. Follow it top to bottom:
        <strong> CV Analysis → Result → Application → Interview → Cover Letter → Package</strong>.
      </p>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '0.875rem', marginBottom: '2rem' }}>
        {FAQS.map((item, i) => (
          <div
            key={i}
            style={{ border: '1px solid var(--color-border)', borderRadius: 'var(--radius-md)', padding: '1rem 1.25rem', background: 'var(--color-surface, #fff)' }}
          >
            <div style={{ fontSize: 'var(--font-size-base)', fontWeight: 700, color: 'var(--color-text)', marginBottom: '0.375rem' }}>
              {item.q}
            </div>
            <p style={{ fontSize: 'var(--font-size-sm)', color: 'var(--color-text-secondary)', lineHeight: 1.7, margin: 0 }}>
              {item.a}
            </p>
          </div>
        ))}
      </div>

      <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.75rem', fontSize: 'var(--font-size-sm)' }}>
        <Link href="/dashboard" style={{ color: 'var(--color-primary)', textDecoration: 'none' }}>CV Analysis</Link>
        <span style={{ color: 'var(--color-text-muted)' }}>·</span>
        <Link href="/applications" style={{ color: 'var(--color-primary)', textDecoration: 'none' }}>Applications</Link>
        <span style={{ color: 'var(--color-text-muted)' }}>·</span>
        <Link href="/profile/evidence" style={{ color: 'var(--color-primary)', textDecoration: 'none' }}>Evidence Vault</Link>
        <span style={{ color: 'var(--color-text-muted)' }}>·</span>
        <Link href="/learning" style={{ color: 'var(--color-primary)', textDecoration: 'none' }}>Learning</Link>
      </div>
    </PageShell>
  );
}

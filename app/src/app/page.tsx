"use client";
import { useEffect, useState } from "react";
import styles from "./page.module.css";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "https://your-railway-app.railway.app";
const NARRATIVES = ["all","DeFi","AI agents","social","memecoins","creator tools","infrastructure","gaming","NFT","other"];
const SCORE_COLORS: Record<number, string> = { 5:"#00D395", 4:"#4FC3F7", 3:"#FFB347", 2:"#FF8A65", 1:"#EF5350" };

interface Project {
  id: string; name: string; url: string; source: string;
  narrative: string; score: number; tags: string[];
  summary: string; why_interesting: string; type: string;
}

export default function Home() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [narrative, setNarrative] = useState("all");
  const [minScore, setMinScore] = useState(1);
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState<{ total_projects: number } | null>(null);

  useEffect(() => {
    fetch(`${API_URL}/stats`).then(r => r.json()).then(setStats).catch(() => {});
  }, []);

  useEffect(() => {
    setLoading(true);
    const params = new URLSearchParams({ narrative, min_score: String(minScore), limit: "60" });
    fetch(`${API_URL}/projects?${params}`)
      .then(r => r.json())
      .then(d => setProjects(d.projects || []))
      .catch(() => setProjects([]))
      .finally(() => setLoading(false));
  }, [narrative, minScore]);

  return (
    <main className={styles.main}>
      <header className={styles.header}>
        <div className={styles.headerInner}>
          <div className={styles.logo}>
            <span className={styles.logoMark}>⬡</span>
            <span className={styles.logoText}>Base Scout</span>
          </div>
          {stats && <span className={styles.totalBadge}>{stats.total_projects} projects tracked</span>}
        </div>
      </header>

      <div className={styles.filters}>
        <div className={styles.narrativeScroll}>
          {NARRATIVES.map(n => (
            <button key={n} className={`${styles.pill} ${narrative === n ? styles.pillActive : ""}`} onClick={() => setNarrative(n)}>{n}</button>
          ))}
        </div>
        <div className={styles.scoreFilter}>
          <span className={styles.scoreLabel}>Min score</span>
          {[1,2,3,4,5].map(s => (
            <button key={s} className={`${styles.scorePill} ${minScore === s ? styles.scorePillActive : ""}`}
              onClick={() => setMinScore(s)} style={minScore === s ? { background: SCORE_COLORS[s] } : {}}>
              {s}★
            </button>
          ))}
        </div>
      </div>

      {loading ? (
        <div className={styles.loading}><div className={styles.spinner}/><span>Scanning Base ecosystem…</span></div>
      ) : projects.length === 0 ? (
        <div className={styles.empty}>No projects found. Try adjusting filters.</div>
      ) : (
        <div className={styles.grid}>
          {projects.map(p => (
            <a key={p.id} href={p.url} target="_blank" rel="noopener noreferrer" className={styles.card}>
              <div className={styles.cardHeader}>
                <div className={styles.cardMeta}>
                  <span className={styles.narrativeBadge}>{p.narrative}</span>
                  <span className={styles.scoreChip} style={{ background: SCORE_COLORS[p.score] || "#888" }}>{p.score}★</span>
                </div>
                <span className={styles.source}>{p.source}</span>
              </div>
              <h3 className={styles.cardTitle}>{p.name}</h3>
              {p.why_interesting && <p className={styles.why}>{p.why_interesting}</p>}
              {p.summary && <p className={styles.summary}>{p.summary}</p>}
              {p.tags?.length > 0 && (
                <div className={styles.tags}>{p.tags.map(t => <span key={t} className={styles.tag}>{t}</span>)}</div>
              )}
            </a>
          ))}
        </div>
      )}
    </main>
  );
}

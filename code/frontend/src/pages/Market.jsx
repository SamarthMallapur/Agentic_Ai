import { Alert, Bar, Card, Citations, Confidence, DataNotice, Loading, Page, useLoad } from '../ui'

export function Claims({ claims }) {
  return (
    <ul className="plain claims">
      {claims.map((c) => (
        <li key={c.id}><div className="claim-line"><span><strong>{c.id}.</strong> {c.text}</span><Confidence level={c.confidence} /></div>
          <div className="muted small">{c.evidence}</div><Citations claim={c} /></li>
      ))}
    </ul>
  )
}

export default function Market() {
  const { data, error, loading } = useLoad('/market')
  if (loading) return <Loading text="Researching postings..." />
  if (error) return <Alert kind="error">{error}</Alert>
  return (
    <Page title="Market Trends" intro={`Based on ${data.sample_size} postings for: ${data.scope}.`}>
      <DataNotice dataset={data.dataset} />
      <div className="grid two">
        <Card title="Most requested skills" note="Share of postings. Darker bars are on your profile.">
          {data.top_skills.map((s) => <Bar key={s.skill} label={s.skill} value={s.pct} muted={!s.student_has} text={`${s.pct}% ${s.student_has ? '· have' : '· gap'}`} />)}
        </Card>
        <Card title="How this was researched">
          <ol className="steps compact">
            {data.research_trace.map((t, i) => <li key={i}><strong>{t.step}</strong> <span className="muted">{Object.entries(t).filter(([k]) => k !== 'step').map(([k, v]) => `${k.replaceAll('_', ' ')}: ${v}`).join(', ')}</span></li>)}
          </ol>
          <p className="muted small">Sources: {data.dataset.sources.join(', ')}</p>
        </Card>
      </div>
      <Card title="Findings" note="Open a source to read the posting behind a claim."><Claims claims={data.claims} /></Card>
    </Page>
  )
}

import { useEffect, useState } from 'react'
import { useSearchParams } from 'react-router-dom'
import { Check, X } from 'lucide-react'
import { api } from '../api'
import { Alert, Bar, Card, Confidence, Page, Tag, useLoad } from '../ui'

function Recommendation({ rec, context }) {
  const [decision, setDecision] = useState('')
  const [rejecting, setRejecting] = useState(false)
  const [reason, setReason] = useState('')
  const save = async (value) => {
    await api.post('/feedback', { suggestion: rec.text, decision: value, skill: rec.skill, reason, context })
    setDecision(value); setRejecting(false)
  }
  return (
    <li className="rec">
      <div>{rec.text} {rec.memory_note && <span className="muted small">{rec.memory_note}</span>}<div className="muted small">{rec.basis}</div></div>
      {decision ? <Tag kind={decision === 'accepted' ? 'good' : 'bad'}>{decision}</Tag> : rejecting ? (
        <div className="reject"><input aria-label="Reason" placeholder="Why? (optional)" value={reason} onChange={(e) => setReason(e.target.value)} /><button onClick={() => save('rejected')}>Save</button></div>
      ) : (
        <div className="rec-actions"><button onClick={() => save('accepted')}><Check size={15} /> Accept</button><button onClick={() => setRejecting(true)}><X size={15} /> Reject</button></div>
      )}
    </li>
  )
}

const Skills = ({ title, items, kind }) => (
  <div className="skill-group"><h3>{title} ({items.length})</h3><div className="tags">{items.length ? items.map((i) => <Tag key={i.skill} kind={kind}>{i.skill}{kind === 'bad' ? ` · ${i.priority}` : ''}</Tag>) : <span className="muted small">None</span>}</div></div>
)

function Result({ r }) {
  return (
    <>
      <Card>
        <div className="result-head">
          <div className="hero-number">{r.total}<small>/100</small></div>
          <div><strong>{r.role || 'Role not given'}{r.company ? ` at ${r.company}` : ''}</strong><div><Confidence level={r.confidence} /></div><p className="muted small">{r.confidence_reason}</p></div>
        </div>
        {r.breakdown.map((b) => <div key={b.criterion}><Bar label={b.criterion} value={b.score} max={b.max} text={`${b.score}/${b.max}`} /><p className="muted small why">{b.why}</p></div>)}
      </Card>
      <Card title="Keyword match"><Skills title="Matched" items={r.gap.matched} kind="good" /><Skills title="Related skill found" items={r.gap.partial} kind="warn" /><Skills title="Missing" items={r.gap.missing} kind="bad" /></Card>
      <Card title="Recommendations" note="Accept or reject each one. The app remembers your decision.">
        <ul className="plain">{r.recommendations.map((rec) => <Recommendation key={rec.id} rec={rec} context={`review ${r.review_id}`} />)}</ul>
        {r.hidden_by_memory.length > 0 && <Alert>Hidden because you rejected similar advice: {r.hidden_by_memory.map((h) => `${h.skill || h.text} (${h.memory_reason})`).join('; ')}</Alert>}
      </Card>
      <div className="grid two">
        <Card title="Formatting checklist"><ul className="plain check">{r.checklist.map((c) => <li key={c.item}>{c.passed ? <Check size={15} className="ok" /> : <X size={15} className="no" />} <span>{c.item}{c.passed ? '' : ' (not met)'}</span></li>)}</ul></Card>
        <Card title="Red flags">{r.red_flags.length ? <ul className="plain">{r.red_flags.map((f) => <li key={f.flag}><strong>{f.flag}.</strong> {f.fix}</li>)}</ul> : <p className="muted">No red flags found.</p>}</Card>
      </div>
      <Card title="Suggested bullet rewrites" note={`${r.qa.rewrite_source}. ${r.qa.rewrites_rejected.length} rejected for adding skills or numbers.`}>
        {r.rewrites.length ? r.rewrites.map((w) => <div className="rewrite" key={w.original}><p className="muted">{w.original}</p><p>{w.rewrite}</p></div>) : <p className="muted">No rewrites for this review.</p>}
      </Card>
    </>
  )
}

export default function Review() {
  const [params] = useSearchParams()
  const apps = useLoad('/applications')
  const profile = useLoad('/profile')
  const latest = useLoad('/review/latest')
  const [form, setForm] = useState({ application_id: '', company: '', role: '', jd: '', resume_text: '' })
  const [result, setResult] = useState(null)
  const [busy, setBusy] = useState(false)
  const [problem, setProblem] = useState('')

  const choose = (id) => {
    const app = apps.data?.find((a) => String(a.id) === String(id))
    setForm((f) => ({ ...f, application_id: id, company: app?.company || '', role: app?.role || '', jd: app?.job_description || '' }))
    setResult(null)
  }
  useEffect(() => { if (profile.data) setForm((f) => ({ ...f, resume_text: f.resume_text || profile.data.resume_text })) }, [profile.data])
  useEffect(() => { if (apps.data && params.get('app')) choose(params.get('app')) }, [apps.data]) // eslint-disable-line

  const submit = async (continueAnyway = false) => {
    setBusy(true); setProblem('')
    try { setResult(await api.post('/review', { ...form, application_id: form.application_id ? Number(form.application_id) : null, continue_anyway: continueAnyway })) }
    catch (e) { setProblem(e.message) } finally { setBusy(false) }
  }
  const field = (key) => ({ value: form[key], onChange: (e) => setForm({ ...form, [key]: e.target.value }) })
  const shown = result || (!params.get('app') && !form.jd ? latest.data : null)

  return (
    <Page title="Resume Review" intro="Compare your resume with one job, using a fixed 100-point rubric.">
      <Card>
        <div className="form-grid">
          <label className="wide">Tracked application<select value={form.application_id} onChange={(e) => choose(e.target.value)}><option value="">Not linked to an application</option>{apps.data?.map((a) => <option key={a.id} value={a.id}>{a.company}: {a.role}</option>)}</select></label>
          <label>Company<input {...field('company')} /></label>
          <label>Role<input {...field('role')} /></label>
          <label>Job description<textarea rows="10" {...field('jd')} /></label>
          <label>Resume<textarea rows="10" {...field('resume_text')} /></label>
        </div>
        <button className="primary" disabled={busy} onClick={() => submit()}>{busy ? 'Reviewing...' : 'Review my resume'}</button>
        <Alert kind="error">{problem}</Alert>
      </Card>
      {result?.status === 'needs_input' ? (
        <Card title="A few details first">
          <ul className="plain">{result.questions.map((q) => <li key={q.field}>{q.question}</li>)}</ul>
          {result.can_continue && <button onClick={() => submit(true)}>Continue anyway (Low confidence)</button>}
        </Card>
      ) : shown?.status === 'done' && <><h2 className="section-title">{result ? 'Your result' : 'Latest review'}</h2><Result r={shown} /></>}
    </Page>
  )
}

import { useState } from 'react'
import { Check, Download, Radio, X } from 'lucide-react'
import { api } from '../api'
import { Alert, Card, Confidence, CountUp, DataNotice, Loading, Page, toast, useLoad } from '../ui'
import { Claims } from './Market'

const AGENTS = ['Resume-Reviewer', 'Interview-Coach', 'Market-Analyst (research loop)']
const RESEARCH = ['search', 'extract', 'compare', 'synthesize']

function Node({ name, label = name, state, children }) {
  const info = state[name] || {}
  return <div className={`node ${info.state || ''}`}>{label}<small>{info.state === 'done' ? `${info.ms} ms` : info.state === 'running' ? 'working' : 'waiting'}</small>{children}</div>
}

function Mission({ nodes, steps, active }) {
  return (
    <Card title="Mission control" note={active ? 'These are live events from the running agents.' : 'Timeline of the latest run.'}>
      <div className="mission">
        <Node name="Load memory" label="Memory" state={nodes} />
        <div className="swarm">
          {AGENTS.map((name) => <Node key={name} name={name} label={name.replace(' (research loop)', '')} state={nodes}>
            {name.startsWith('Market') && <div className="research-steps">{RESEARCH.map((s) => <span key={s} className={steps.includes(s) ? 'on' : ''}>{s}</span>)}</div>}
          </Node>)}
        </div>
        <Node name="Merge" state={nodes} /><Node name="Write summary" label="Summary" state={nodes} /><Node name="QA gate" label="QA" state={nodes} />
        <div className={`node ${nodes.final ? 'done' : ''}`}>Report<small>{nodes.final ? 'ready' : 'waiting'}</small></div>
      </div>
      <div className={`flow-line ${active ? 'live' : ''}`} />
    </Card>
  )
}

const completedNodes = (report) => report ? { ...Object.fromEntries(report.trace.map((t) => [t.node, { state: 'done', ms: t.ms }])), final: true } : {}

export default function Report() {
  const { data: report, setData, loading } = useLoad('/report/latest')
  const [busy, setBusy] = useState(false)
  const [problem, setProblem] = useState('')
  const [live, setLive] = useState(null)

  const generate = async () => {
    setBusy(true); setProblem(''); setLive({ nodes: {}, steps: [] })
    try {
      const response = await fetch('/api/report/stream', { method: 'POST' })
      if (!response.ok || !response.body) throw new Error('The report could not be started.')
      const reader = response.body.pipeThrough(new TextDecoderStream()).getReader()
      let buffer = ''
      for (;;) {
        const { value, done } = await reader.read()
        if (done) break
        buffer += value
        const lines = buffer.split('\n'); buffer = lines.pop()
        for (const line of lines.filter(Boolean)) {
          const event = JSON.parse(line)
          if (event.type === 'node') setLive((v) => ({ ...v, nodes: { ...v.nodes, [event.node]: event } }))
          if (event.type === 'research') setLive((v) => ({ ...v, steps: [...v.steps, event.step] }))
          if (event.type === 'error') throw new Error(event.detail)
          if (event.type === 'report') { setData(event.report); setLive((v) => ({ ...v, nodes: { ...v.nodes, final: true } })); toast('Weekly report is ready') }
        }
      }
    } catch (e) { setProblem(e.message) } finally { setBusy(false) }
  }
  const nodes = live?.nodes || completedNodes(report), steps = live?.steps || (report ? RESEARCH : [])
  const action = (
    <div className="head-actions">
      {report && <a className="button" href="/api/report/latest.md"><Download size={15} /> Download</a>}
      <button className="primary" disabled={busy} onClick={generate}><Radio size={15} /> {busy ? 'Agents working...' : 'Generate new report'}</button>
    </div>
  )
  return (
    <Page title="Weekly Report" intro="Watch three agents work in parallel, then merge and pass QA." action={action}>
      <Alert kind="error">{problem}</Alert>
      {(report || live) && <Mission nodes={nodes} steps={steps} active={busy} />}
      {loading ? <Loading /> : !report ? !live && <Card><p className="muted">No report yet. Press Generate new report.</p></Card> : (
        <>
          <DataNotice dataset={report.market.dataset} />
          <Card><h2>Readiness <CountUp value={report.readiness.score} />/100</h2><p className="muted small">Generated {report.generated_at.replace('T', ' ')}</p><p>{report.summary}</p><p className="muted small">Summary source: {report.summary_source}</p></Card>
          <Card title="Recommended actions"><ol className="steps">{report.actions.map((a) => <li key={a.action}><strong>{a.action}</strong> {a.why}<div className="muted small">Basis: {a.basis} <Confidence level={a.confidence} /></div></li>)}</ol></Card>
          <div className="grid three">
            <Card title="Resume-Reviewer">{report.resume.reviewed?.length ? <><div className="stat-line">{report.resume.average}/100 average</div><ul className="plain">{report.resume.reviewed.map((r) => <li key={r.application_id}>{r.score}/100, {r.role}</li>)}</ul></> : <p className="muted">{report.resume.note}</p>}</Card>
            <Card title="Interview-Coach">{report.interview.attempts ? <><div className="stat-line">{report.interview.average}/10 average</div><p>{report.interview.attempts} answer(s) saved.</p><Confidence level={report.interview.confidence} /></> : <p className="muted">{report.interview.note}</p>}</Card>
            <Card title="Market-Analyst"><div className="stat-line">{report.market.sample_size} postings</div><p>{report.market.claims.length} verified claims.</p><p className="muted small">Connector: {report.market.transport}</p></Card>
          </div>
          <Card title="Market findings"><Claims claims={report.market.claims} /></Card>
          <Card title="Evidence table"><div className="table-wrap"><table><thead><tr><th>ID</th><th>Claim</th><th>Evidence</th><th>Source</th><th>n</th><th>Confidence</th></tr></thead><tbody>{report.evidence_table.map((e) => <tr key={e.id}><td>{e.id}</td><td>{e.claim}</td><td>{e.evidence}</td><td className="small">{e.source}</td><td>{e.sample}</td><td>{e.confidence}</td></tr>)}</tbody></table></div></Card>
          <Card title="QA checks"><ul className="plain check">{report.qa.map((q) => <li key={q.check}>{q.passed ? <Check size={15} className="ok" /> : <X size={15} className="no" />}<span>{q.passed ? 'Passed' : 'Failed'}: {q.check}<span className="muted small"> {q.detail}</span></span></li>)}</ul></Card>
        </>
      )}
    </Page>
  )
}

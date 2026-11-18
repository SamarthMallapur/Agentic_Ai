import { useState } from 'react'
import { Check, Download, X } from 'lucide-react'
import { api } from '../api'
import { Alert, Card, Confidence, DataNotice, Loading, Page, useLoad } from '../ui'
import { Claims } from './Market'

export default function Report() {
  const { data: report, setData, loading } = useLoad('/report/latest')
  const [busy, setBusy] = useState(false)
  const [problem, setProblem] = useState('')
  const generate = async () => {
    setBusy(true); setProblem('')
    try { setData(await api.post('/report')) } catch (e) { setProblem(e.message) } finally { setBusy(false) }
  }
  const action = (
    <div className="head-actions">
      {report && <a className="button" href="/api/report/latest.md"><Download size={15} /> Download</a>}
      <button className="primary" disabled={busy} onClick={generate}>{busy ? 'Agents are working...' : 'Generate new report'}</button>
    </div>
  )
  return (
    <Page title="Weekly Report" intro="Three agents work in parallel. Their results are merged and checked before you see them." action={action}>
      <Alert kind="error">{problem}</Alert>
      {loading ? <Loading /> : !report ? <Card><p className="muted">No report yet. Press Generate new report.</p></Card> : (
        <>
          <DataNotice dataset={report.market.dataset} />
          <Card title={`Readiness ${report.readiness.score}/100`} note={`Generated ${report.generated_at.replace('T', ' ')}`}>
            <p>{report.summary}</p><p className="muted small">Summary source: {report.summary_source}</p>
          </Card>
          <Card title="Recommended actions">
            <ol className="steps">{report.actions.map((a) => <li key={a.action}><strong>{a.action}</strong> {a.why}<div className="muted small">Basis: {a.basis} <Confidence level={a.confidence} /></div></li>)}</ol>
          </Card>
          <div className="grid three">
            <Card title="Resume-Reviewer">{report.resume.reviewed?.length ? <><div className="stat-line">{report.resume.average}/100 average</div><ul className="plain">{report.resume.reviewed.map((r) => <li key={r.application_id}>{r.score}/100, {r.role}</li>)}</ul></> : <p className="muted">{report.resume.note}</p>}</Card>
            <Card title="Interview-Coach">{report.interview.attempts ? <><div className="stat-line">{report.interview.average}/10 average</div><p>{report.interview.attempts} answer(s) saved.</p><Confidence level={report.interview.confidence} /></> : <p className="muted">{report.interview.note}</p>}</Card>
            <Card title="Market-Analyst"><div className="stat-line">{report.market.sample_size} postings</div><p>{report.market.claims.length} verified claims.</p><p className="muted small">Connector: {report.market.transport}</p></Card>
          </div>
          <Card title="Market findings"><Claims claims={report.market.claims} /></Card>
          <Card title="Evidence table">
            <div className="table-wrap"><table><thead><tr><th>ID</th><th>Claim</th><th>Evidence</th><th>Source</th><th>n</th><th>Confidence</th></tr></thead>
              <tbody>{report.evidence_table.map((e) => <tr key={e.id}><td>{e.id}</td><td>{e.claim}</td><td>{e.evidence}</td><td className="small">{e.source}</td><td>{e.sample}</td><td>{e.confidence}</td></tr>)}</tbody></table></div>
          </Card>
          <div className="grid two">
            <Card title="QA checks"><ul className="plain check">{report.qa.map((q) => <li key={q.check}>{q.passed ? <Check size={15} className="ok" /> : <X size={15} className="no" />}<span>{q.passed ? 'Passed' : 'Failed'}: {q.check}<span className="muted small"> {q.detail}</span></span></li>)}</ul></Card>
            <Card title="Run trace"><ul className="plain">{report.trace.map((t) => <li key={t.node} className="trace"><span>{t.node}</span><span className="muted">{t.ms} ms</span></li>)}</ul></Card>
          </div>
        </>
      )}
    </Page>
  )
}

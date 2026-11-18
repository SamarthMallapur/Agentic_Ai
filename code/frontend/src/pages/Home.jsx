import { Link } from 'react-router-dom'
import { Alert, Bar, Card, CountUp, DataNotice, Loading, Page, Ring, useLoad } from '../ui'

const STEPS = [
  ['/profile', 'Check your profile', 'Add your resume, skills and target roles.'],
  ['/applications', 'Track applications', 'Save each job and its description.'],
  ['/review', 'Review your resume', 'Get a fixed-rubric score and test improvements.'],
  ['/interview', 'Practise interviews', 'Answer against the clock, by typing or speaking.'],
  ['/compass', 'Open Career Compass', 'See what to learn next and which jobs fit.'],
  ['/report', 'Generate your weekly report', 'Watch the agents build one cited plan.'],
]

function Trend({ points }) {
  if (points.length < 2) return <p className="muted small">Generate two weekly reports to see your readiness trend.</p>
  const x = (i) => 8 + (i * 284) / (points.length - 1), y = (score) => 68 - score * 0.6
  return (
    <>
      <svg className="trend" viewBox="0 0 300 76" preserveAspectRatio="none" role="img" aria-label={`Readiness moved from ${points[0].score} to ${points.at(-1).score}`}>
        <polyline points={points.map((p, i) => `${x(i)},${y(p.score)}`).join(' ')} />
        {points.map((p, i) => <circle key={p.report_id} cx={x(i)} cy={y(p.score)} r="4"><title>{`${p.at.slice(0, 10)}: ${p.score}/100`}</title></circle>)}
      </svg>
      <p className="muted small">Latest {points.at(-1).score}/100 across {points.length} reports.</p>
    </>
  )
}

export default function Home() {
  const { data, error, loading } = useLoad('/dashboard')
  const history = useLoad('/readiness/history')
  if (loading) return <Loading />
  if (error) return <Alert kind="error">{error}</Alert>
  const { readiness, tracker, coach } = data
  const stats = [['Applications', tracker.total], ['Interviews', tracker.by_status.INTERVIEW || 0], ['Offers', tracker.by_status.OFFER || 0], ['Mock answers', coach.attempts]]
  return (
    <Page title={`Hello, ${data.student || 'student'}`} intro="Here is where your placement preparation stands today.">
      <DataNotice dataset={data.dataset} />
      <div className="grid two">
        <Card title="Readiness">
          <div className="readiness">
            <Ring value={readiness.score} />
            <div>{readiness.parts.map((p) => p.value === null ? <Bar key={p.name} label={p.name} value={0} text="No data" muted /> : <Bar key={p.name} label={p.name} value={p.value} text={`${p.value}`} />)}</div>
          </div>
          <p className="muted small">Weights: resume 40, market skills 30, interview 20, activity 10. Parts with no data are left out.</p>
        </Card>
        <Card title="This season">
          <div className="stats">{stats.map(([label, value]) => <div key={label}><b><CountUp value={value} /></b><span>{label}</span></div>)}</div>
          {tracker.follow_ups_due.length > 0 && <Alert kind="warn">{tracker.follow_ups_due.length} follow-up(s) are due. <Link to="/applications">Open applications</Link></Alert>}
          {data.top_gap && <p><strong>Biggest market gap:</strong> {data.top_gap.text}</p>}
          <h3>Readiness trend</h3>
          <Trend points={history.data || []} />
        </Card>
      </div>
      <Card title="How to use this app">
        <ol className="steps">{STEPS.map(([to, title, text]) => <li key={to}><Link to={to}>{title}</Link><span className="muted"> {text}</span></li>)}</ol>
      </Card>
    </Page>
  )
}

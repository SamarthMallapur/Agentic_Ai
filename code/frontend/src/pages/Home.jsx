import { Link } from 'react-router-dom'
import { Alert, Bar, Card, DataNotice, Loading, Page, useLoad } from '../ui'

const STEPS = [
  ['/profile', 'Check your profile', 'Add your resume, skills and target roles.'],
  ['/applications', 'Track applications', 'Save each job and its description.'],
  ['/review', 'Review your resume', 'Get a fixed-rubric score for one job.'],
  ['/interview', 'Practise interviews', 'Answer questions and get feedback.'],
  ['/report', 'Generate your weekly report', 'See one cited plan for the week.'],
]

export default function Home() {
  const { data, error, loading } = useLoad('/dashboard')
  if (loading) return <Loading />
  if (error) return <Alert kind="error">{error}</Alert>
  const { readiness, tracker, coach } = data
  return (
    <Page title={`Hello, ${data.student || 'student'}`} intro="Here is where your placement preparation stands today.">
      <DataNotice dataset={data.dataset} />
      <div className="grid two">
        <Card title="Readiness">
          <div className="hero-number">{readiness.score}<small>/100</small></div>
          {readiness.parts.map((p) => p.value === null
            ? <Bar key={p.name} label={p.name} value={0} text="No data" muted />
            : <Bar key={p.name} label={p.name} value={p.value} text={`${p.value}`} />)}
          <p className="muted small">Weights: resume 40, market skills 30, interview 20, activity 10. Parts with no data are left out.</p>
        </Card>
        <Card title="This season">
          <div className="stats">
            <div><b>{tracker.total}</b><span>Applications</span></div>
            <div><b>{tracker.by_status.INTERVIEW || 0}</b><span>Interviews</span></div>
            <div><b>{tracker.by_status.OFFER || 0}</b><span>Offers</span></div>
            <div><b>{coach.attempts}</b><span>Mock answers</span></div>
          </div>
          {tracker.follow_ups_due.length > 0 && <Alert kind="warn">{tracker.follow_ups_due.length} follow-up(s) are due. <Link to="/applications">Open applications</Link></Alert>}
          {data.top_gap && <p><strong>Biggest market gap:</strong> {data.top_gap.text}</p>}
        </Card>
      </div>
      <Card title="How to use this app">
        <ol className="steps">
          {STEPS.map(([to, title, text]) => <li key={to}><Link to={to}>{title}</Link><span className="muted"> {text}</span></li>)}
        </ol>
      </Card>
    </Page>
  )
}

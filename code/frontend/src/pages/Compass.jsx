import { useState } from 'react'
import { Plus } from 'lucide-react'
import { api } from '../api'
import { Alert, Bar, Card, Citations, Confidence, DataNotice, Loading, Page, Tag, toast, useLoad } from '../ui'

function Job({ job }) {
  const [added, setAdded] = useState(false)
  const track = async () => {
    try {
      await api.post('/applications', { company: job.company || 'Company not listed', role: job.title, job_description: job.description })
      setAdded(true); toast(`${job.title} added to Applications`)
    } catch (e) { toast(e.message) }
  }
  return (
    <Card>
      <div className="card-top"><div><strong>{job.title}</strong><div className="muted small">{job.company || 'Company not listed'} · {job.location || 'Location not listed'}</div></div><span className="match">{job.match_pct}%</span></div>
      <Bar label="JD skill match" value={job.match_pct} text={`${job.match_pct}%`} />
      <div className="tags">{job.matched.slice(0, 5).map((s) => <Tag kind="good" key={s}>{s}</Tag>)}{job.missing.slice(0, 3).map((s) => <Tag kind="bad" key={s}>Needs {s}</Tag>)}</div>
      <p className="muted small">Source: {job.source}, row {job.source_row}</p>
      <button disabled={added} onClick={track}><Plus size={15} /> {added ? 'Tracked' : 'Track this job'}</button>
    </Card>
  )
}

export default function Compass() {
  const roadmap = useLoad('/roadmap')
  const jobs = useLoad('/job-matches')
  if (roadmap.loading || jobs.loading) return <Loading text="Finding your best next moves" />
  if (roadmap.error || jobs.error) return <Alert kind="error">{roadmap.error || jobs.error}</Alert>
  return (
    <Page title="Career Compass" intro="Your best next skills and closest job matches, ranked from your own data.">
      <DataNotice dataset={roadmap.data.dataset} />
      <h2 className="section-title">Skill roadmap</h2>
      <p className="muted small">{roadmap.data.method}</p>
      <div className="compass-grid">
        {roadmap.data.items.map((item, index) => (
          <Card key={item.skill}>
            <div className="card-top"><h2><span className="rank">{index + 1}</span>{item.skill}</h2><Confidence level={item.confidence} /></div>
            <Bar label="Priority" value={item.priority_score} text={`${item.priority_score}/100`} />
            <p className="small">{item.demand_pct}% of {roadmap.data.sample_size} postings. Needed by {item.needed_by_applications.length} tracked job(s). {item.effort}.</p>
            {item.related_skills_you_have.length > 0 && <p className="muted small">Head start: {item.related_skills_you_have.join(', ')}</p>}
            {item.previously_rejected && <Alert kind="warn">You said: {item.previously_rejected}. This is a learning idea, not resume advice.</Alert>}
            <ol className="steps compact">{item.plan.map((step) => <li key={step}>{step}</li>)}</ol>
            <Citations claim={item} />
          </Card>
        ))}
      </div>
      <h2 className="section-title">Best-fit jobs you are not tracking</h2>
      {jobs.data.items.length ? <div className="compass-grid">{jobs.data.items.map((job) => <Job key={job.posting_id} job={job} />)}</div> : <Card><p className="muted">No new matches were found.</p></Card>}
    </Page>
  )
}

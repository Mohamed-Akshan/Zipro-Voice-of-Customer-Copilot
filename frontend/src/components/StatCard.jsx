export default function StatCard({ label, value, caption, icon: Icon, variant = 'blue' }) {
  return (
    <div className="stat-card">
      <div className="stat-heading"><span>{label}</span><span className={`stat-icon ${variant}`}><Icon size={19}/></span></div>
      <div className="stat-value">{value}</div>
      <div className="stat-caption">{caption}</div>
    </div>
  )
}

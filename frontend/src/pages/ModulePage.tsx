
interface ModulePageProps {
  title: string;
  description: string;
}

export default function ModulePage({
  title,
  description,
}: ModulePageProps) {
  return (
    <div className="dashboard-page">
      <div className="welcome-section">
        <div>
          <h1>{title}</h1>
          <p>{description}</p>
        </div>
      </div>

      <div className="chart-card">
        <h3>{title}</h3>
        <p>
          This module is ready for development.
          We'll add its functionality in the next steps.
        </p>
      </div>
    </div>
  );
}

'use client';

interface StatsCardProps {
  title: string;
  value: string | number;
  icon?: React.ReactNode;
  description?: string;
  gradient?: 'primary' | 'success' | 'warning' | 'info';
}

export default function StatsCard({ title, value, icon, description, gradient = 'primary' }: StatsCardProps) {
  const gradientClasses = {
    primary: 'from-blue-500 to-purple-600',
    success: 'from-green-500 to-emerald-600',
    warning: 'from-yellow-500 to-orange-600',
    info: 'from-cyan-500 to-blue-600',
  };

  return (
    <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6 border border-gray-200 dark:border-gray-700 card-hover">
      <div className="flex items-center justify-between mb-4">
        <div className={`p-3 rounded-lg bg-gradient-to-br ${gradientClasses[gradient]} text-white`}>
          {icon}
        </div>
        <div className="text-right">
          <p className="text-sm font-medium text-gray-600 dark:text-gray-400">{title}</p>
          <p className="text-3xl font-bold text-gray-900 dark:text-white mt-1">{value}</p>
        </div>
      </div>
      {description && (
        <p className="text-xs text-gray-500 dark:text-gray-500 mt-2">{description}</p>
      )}
    </div>
  );
}

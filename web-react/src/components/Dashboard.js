import React from 'react';
import BuildingModel from './BuildingModel';
import EnvironmentalStatus from './EnvironmentalStatus';
import AlertsPanel from './AlertsPanel';
import PredictionsChart from './PredictionsChart';
import TrendAnalysis from './TrendAnalysis';

const Dashboard = () => {
  return (
    <section className="dashboard-grid">
      <BuildingModel />
      <EnvironmentalStatus />
      <AlertsPanel />
      <PredictionsChart />
      <TrendAnalysis />
    </section>
  );
};

export default Dashboard;

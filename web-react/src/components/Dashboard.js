import React from 'react';
import ErrorBoundary from './ErrorBoundary';
import ClimateDigitalTwin from './ClimateDigitalTwin';
import EnvironmentalStatus from './EnvironmentalStatus';
import AlertsPanel from './AlertsPanel';
import TrendAnalysis from './TrendAnalysis';
import RoomDetails from './RoomDetails';
import PredictiveAnalysis from './PredictiveAnalysis';
import AutomationControls from './AutomationControls';
import ClimateInsights from './ClimateInsights';

const Dashboard = () => {
  return (
    <>
      {/* Climate Digital Twin Visualization */}
      <section className="dashboard-grid">
        <ErrorBoundary>
          <ClimateDigitalTwin />
        </ErrorBoundary>
        <EnvironmentalStatus />
        <AlertsPanel />
      </section>

      {/* Trend Analysis Grid */}
      <section className="dashboard-grid">
        <ErrorBoundary>
          <TrendAnalysis />
        </ErrorBoundary>
      </section>
      
      {/* AI Climate Insights Section */}
      <ErrorBoundary>
        <ClimateInsights />
      </ErrorBoundary>
      
      {/* Room Details Section */}
      <RoomDetails />
      
      {/* Predictive Analysis Section */}
      <ErrorBoundary>
        <PredictiveAnalysis />
      </ErrorBoundary>
      
      {/* Automation Controls Section */}
      <AutomationControls />
    </>
  );
};

export default Dashboard;

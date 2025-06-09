import React from 'react';
import ErrorBoundary from './ErrorBoundary';
import BuildingModel from './BuildingModel';
import EnvironmentalStatus from './EnvironmentalStatus';
import AlertsPanel from './AlertsPanel';
import TrendAnalysis from './TrendAnalysis';
import RoomDetails from './RoomDetails';
import PredictiveAnalysis from './PredictiveAnalysis';
import AutomationControls from './AutomationControls';

const Dashboard = () => {
  return (
    <>
      {/* Dashboard Overview Grid */}
      <section className="dashboard-grid">
        <BuildingModel />
        <EnvironmentalStatus />
        <AlertsPanel />
        <ErrorBoundary>
          <TrendAnalysis />
        </ErrorBoundary>
      </section>
      
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

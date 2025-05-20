import React from 'react';
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
        <TrendAnalysis />
      </section>
      
      {/* Room Details Section */}
      <RoomDetails />
      
      {/* Predictive Analysis Section */}
      <PredictiveAnalysis />
      
      {/* Automation Controls Section */}
      <AutomationControls />
    </>
  );
};

export default Dashboard;

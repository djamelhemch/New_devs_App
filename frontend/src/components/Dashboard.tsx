import React, { useEffect, useState } from "react";
import { RevenueSummary } from "./RevenueSummary";
import { supabase } from "../lib/supabase"; // ✅ Import supabase client
import { SecureAPI } from "../lib/secureApi"; // ✅ Import the new API client
//const PROPERTIES = [
//   { id: 'prop-001', name: 'Beach House Alpha' },
//   { id: 'prop-002', name: 'City Apartment Downtown' },
//   { id: 'prop-003', name: 'Country Villa Estate' },
//   { id: 'prop-004', name: 'Lakeside Cottage' },
//   { id: 'prop-005', name: 'Urban Loft Modern' }
// ];
interface Property {
  id: string;
  name: string;
  timezone?: string;
}

const Dashboard: React.FC = () => {
  const [selectedProperty, setSelectedProperty] = useState('');
  const [properties, setProperties] = useState<Property[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

useEffect(() => {
  const fetchProperties = async () => {
    try {
      setError(null);
      console.log('🔍 Fetching properties...');
      
      const result = await SecureAPI.getProperties();
      console.log('📦 Result:', result);
      
      // Handle the {data: [], total: n} format
      const propertiesList = result?.data || [];
      console.log('🏠 Properties:', propertiesList);
      
      setProperties(propertiesList);
      
      if (propertiesList.length > 0) {
        setSelectedProperty(propertiesList[0].id);
      }
    } catch (error) {
      console.error('❌ Error:', error);
      setError('Error loading properties');
    } finally {
      setLoading(false);
    }
  };

  fetchProperties();
}, []);

  if (loading) {
    return (
      <div className="p-6 flex items-center justify-center">
        <div className="text-gray-600">Loading properties...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-6">
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <p className="text-red-800">{error}</p>
        </div>
      </div>
    );
  }

  if (properties.length === 0) {
    return (
      <div className="p-6">
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
          <p className="text-yellow-800">No properties found for your account.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="p-4 lg:p-6 min-h-full">
      <div className="max-w-7xl mx-auto">
        <h1 className="text-2xl font-bold mb-6 text-gray-900">Property Management Dashboard</h1>

        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4 lg:p-6">
          <div className="mb-6">
            <div className="flex flex-col sm:flex-row sm:justify-between sm:items-start gap-4">
              <div>
                <h2 className="text-lg lg:text-xl font-medium text-gray-900 mb-2">Revenue Overview</h2>
                <p className="text-sm lg:text-base text-gray-600">
                  Monthly performance insights for your properties
                </p>
              </div>
              
              {/* Property Selector */}
              <div className="flex flex-col sm:items-end">
                <label className="text-xs font-medium text-gray-700 mb-1">Select Property</label>
                <select
                  value={selectedProperty}
                  onChange={(e) => setSelectedProperty(e.target.value)}
                  className="block w-full sm:w-auto min-w-[200px] px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 text-sm"
                >
                  {properties.map((property) => (
                    <option key={property.id} value={property.id}>
                      {property.name}
                    </option>
                  ))}
                </select>
              </div>
            </div>
          </div>

          <div className="space-y-6">
            {selectedProperty && <RevenueSummary propertyId={selectedProperty} />}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
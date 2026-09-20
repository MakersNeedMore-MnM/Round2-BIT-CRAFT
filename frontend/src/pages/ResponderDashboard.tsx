import { useState, useEffect, useCallback, useRef } from 'react';
import { Link } from 'react-router-dom';
import { storageService } from '../services/storage';
import { sosService } from '../services/api';
import type { NearbyAlert } from '../types';
import {
  ShieldAlert, MapPin, Loader2, AlertCircle,
  RefreshCw, User, Plus, Activity, ChevronRight, CheckCircle, Navigation
} from 'lucide-react';

export function ResponderDashboard() {
  const [alerts, setAlerts] = useState<NearbyAlert[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [acknowledgingId, setAcknowledgingId] = useState<string | null>(null);
  const timersRef = useRef<{ [key: string]: number | ReturnType<typeof setTimeout> }>({});

  const profileId = storageService.getProfileId();

  const fetchAlerts = useCallback(async (showRefreshIndicator = false) => {
    if (!profileId) {
      setIsLoading(false);
      return;
    }

    if (showRefreshIndicator) {
      setIsRefreshing(true);
    } else {
      setIsLoading(true);
    }
    setError(null);

    try {
      const data = await sosService.getNearbyAlerts(profileId);
      const fetchedAlerts = data.nearby_alerts || [];
      setAlerts(fetchedAlerts);

      // Setup expiration timers for initially fetched alerts
      Object.values(timersRef.current).forEach(clearTimeout);
      timersRef.current = {};

      fetchedAlerts.forEach((alert: NearbyAlert) => {
        if (alert.expires_at) {
          const timeUntilExpiry = new Date(alert.expires_at).getTime() - Date.now();
          if (timeUntilExpiry > 0) {
            timersRef.current[alert.alert_id] = setTimeout(() => {
              setAlerts(prev => prev.filter(a => a.alert_id !== alert.alert_id));
            }, timeUntilExpiry);
          }
        }
      });
    } catch (err: any) {
      console.error('Error fetching nearby alerts:', err);
      setError('Could not load nearby alerts. Please check your connection.');
    } finally {
      setIsLoading(false);
      setIsRefreshing(false);
    }
  }, [profileId]);

  useEffect(() => {
    fetchAlerts();

    // Cleanup timers on unmount
    return () => {
      Object.values(timersRef.current).forEach(clearTimeout);
    };
  }, [fetchAlerts]);

  const handleAcknowledge = async (alertId: string) => {
    if (acknowledgingId || !profileId) return;

    setAcknowledgingId(alertId);
    try {
      await sosService.acknowledgeAlert(alertId, profileId);
      // Update local state to reflect acknowledgement
      setAlerts(prev => prev.map(a =>
        a.alert_id === alertId ? { ...a, has_acknowledged: true } : a
      ));
    } catch (err) {
      console.error('Error acknowledging alert:', err);
      alert('Failed to acknowledge the alert. Please try again.');
    } finally {
      setAcknowledgingId(null);
    }
  };

  const handleNavigateToSOS = (alert: NearbyAlert) => {
    const mapsUrl = `https://www.google.com/maps/dir/?api=1&destination=${encodeURIComponent(
      `${alert.latitude},${alert.longitude}`
    )}`;

    window.open(mapsUrl, '_blank', 'noopener,noreferrer');
  };

  // WebSocket Connection
  useEffect(() => {
    if (!profileId) return;

    let ws: WebSocket;
    let reconnectTimeout: number | ReturnType<typeof setTimeout>;

    const connect = () => {
      const apiUrl = import.meta.env.VITE_API_URL || window.location.origin;
      const wsProtocol = apiUrl.startsWith('https') ? 'wss://' : 'ws://';
      const wsHost = apiUrl.replace(/^https?:\/\//, '');
      const wsUrl = `${wsProtocol}${wsHost}/ws/alerts/${profileId}`;

      ws = new WebSocket(wsUrl);

      ws.onmessage = (event) => {
        try {
          const payload = JSON.parse(event.data);

          if (payload.type === 'ALERT_CREATED') {
            const newAlert = payload.data as NearbyAlert;
            setAlerts(prev => {
              // Prevent duplicates if already fetched via REST during WS setup
              if (prev.some(a => a.alert_id === newAlert.alert_id)) return prev;
              return [newAlert, ...prev];
            });

            // Setup expiration timer for the new alert
            if (newAlert.expires_at) {
              const timeUntilExpiry = new Date(newAlert.expires_at).getTime() - Date.now();
              if (timeUntilExpiry > 0) {
                if (timersRef.current[newAlert.alert_id]) {
                  clearTimeout(timersRef.current[newAlert.alert_id]);
                }
                timersRef.current[newAlert.alert_id] = setTimeout(() => {
                  setAlerts(prev => prev.filter(a => a.alert_id !== newAlert.alert_id));
                }, timeUntilExpiry);
              }
            }
          } else if (payload.type === 'ALERT_RESOLVED') {
            const resolvedAlertId = payload.data.alert_id;

            setAlerts(prev => prev.filter(a => a.alert_id !== resolvedAlertId));

            if (timersRef.current[resolvedAlertId]) {
              clearTimeout(timersRef.current[resolvedAlertId]);
              delete timersRef.current[resolvedAlertId];
            }
          }
        } catch (err) {
          console.error("Failed to parse WebSocket message:", err);
        }
      };

      ws.onclose = () => {
        reconnectTimeout = setTimeout(connect, 3000); // Attempt reconnect after 3s
      };
    };

    connect();

    return () => {
      clearTimeout(reconnectTimeout);
      if (ws) {
        ws.onclose = null; // Prevent reconnect on deliberate unmount cleanup
        ws.close();
      }
    };
  }, [profileId]);

  if (!profileId) {
    return (
      <div className="flex flex-col items-center justify-center py-12 gap-6 text-center">
        <div className="w-20 h-20 bg-gray-100 rounded-full flex items-center justify-center">
          <User className="w-10 h-10 text-gray-400" />
        </div>
        <div>
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Profile Required</h2>
          <p className="text-gray-500 max-w-[250px] mx-auto">
            You must create an Emergency E-Card before viewing the responder dashboard.
          </p>
        </div>
        <Link
          to="/create"
          className="bg-brand-600 hover:bg-brand-700 text-white font-bold py-3 px-8 rounded-full transition-colors shadow-sm flex items-center gap-2 mt-4"
        >
          <Plus className="w-5 h-5" />
          Create E-Card
        </Link>
      </div>
    );
  }

  return (
    <div className="py-4 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
            <Activity className="w-6 h-6 text-brand-600" />
            Nearby Alerts
          </h1>
          <p className="text-sm text-gray-500 mt-1">Active emergencies in your area</p>
        </div>
        <button
          onClick={() => fetchAlerts(true)}
          disabled={isLoading || isRefreshing}
          className="p-2.5 text-gray-500 hover:text-brand-600 bg-gray-100 hover:bg-brand-50 rounded-full transition-colors disabled:opacity-50"
          aria-label="Refresh alerts"
        >
          <RefreshCw className={`w-5 h-5 ${isRefreshing ? 'animate-spin text-brand-600' : ''}`} />
        </button>
      </div>

      {isLoading && !isRefreshing ? (
        <div className="flex flex-col items-center justify-center py-20 gap-4">
          <Loader2 className="w-10 h-10 text-brand-500 animate-spin" />
          <p className="text-gray-500 font-medium">Scanning for alerts...</p>
        </div>
      ) : error ? (
        <div className="bg-red-50 border border-red-200 p-6 rounded-2xl flex flex-col items-center text-center gap-4">
          <AlertCircle className="w-12 h-12 text-red-500" />
          <div>
            <h3 className="font-bold text-red-900 text-lg mb-1">Error Loading Alerts</h3>
            <p className="text-sm text-red-700">{error}</p>
          </div>
          <button
            onClick={() => fetchAlerts()}
            className="mt-2 px-6 py-2 bg-red-100 hover:bg-red-200 text-red-800 font-semibold rounded-full transition-colors text-sm"
          >
            Try Again
          </button>
        </div>
      ) : alerts.length === 0 ? (
        <div className="bg-white border border-gray-100 rounded-2xl p-8 flex flex-col items-center text-center gap-4 shadow-sm">
          <div className="w-16 h-16 bg-green-50 rounded-full flex items-center justify-center">
            <ShieldAlert className="w-8 h-8 text-green-500" />
          </div>
          <div>
            <h3 className="font-bold text-gray-900 text-lg mb-1">No Active Alerts</h3>
            <p className="text-sm text-gray-500">There are no reported emergencies in your immediate vicinity right now.</p>
          </div>
        </div>
      ) : (
        <div className="space-y-4">
          {alerts.map((alert) => (
            <div
              key={alert.alert_id}
              className="block bg-white border border-red-100 rounded-2xl shadow-sm relative overflow-hidden group"
            >
              <div className="absolute top-0 left-0 w-1.5 h-full bg-red-500"></div>

              <div className="p-5">
                <div className="flex items-start justify-between mb-4">
                  <div>
                    <h3 className="font-bold text-gray-900 text-lg">
                      {alert.full_name || 'Unknown User'}
                    </h3>
                    <div className="flex items-center gap-1.5 text-gray-500 text-sm mt-1">
                      <MapPin className="w-4 h-4 text-red-500" />
                      <span>{alert.distance_km.toFixed(2)} km away</span>
                    </div>
                  </div>
                  <div className="bg-red-50 text-red-700 text-xs font-bold px-3 py-1.5 rounded-full flex items-center gap-1.5 animate-pulse">
                    <div className="w-2 h-2 bg-red-500 rounded-full"></div>
                    ACTIVE
                  </div>
                </div>

                <div className="flex flex-col gap-3 pt-4 border-t border-gray-100">
                  <div className="flex items-center gap-3">
                    <Link
                      to={`/emergency/${alert.profile_id}`}
                      className="flex-1 bg-gray-50 hover:bg-gray-100 text-gray-700 font-semibold py-2.5 px-4 rounded-xl flex items-center justify-center gap-2 transition-colors text-sm"
                    >
                      View Details
                      <ChevronRight className="w-4 h-4" />
                    </Link>
                  </div>

                  <button
                    onClick={() => handleAcknowledge(alert.alert_id)}
                    disabled={alert.has_acknowledged || acknowledgingId === alert.alert_id}
                    className={`w-full font-semibold py-3 px-4 rounded-xl flex items-center justify-center gap-2 transition-colors text-sm ${
                      alert.has_acknowledged
                        ? 'bg-green-100 text-green-800 border border-green-200'
                        : 'bg-brand-600 hover:bg-brand-700 text-white shadow-sm'
                    } disabled:opacity-80`}
                  >
                    {acknowledgingId === alert.alert_id ? (
                      <Loader2 className="w-5 h-5 animate-spin" />
                    ) : alert.has_acknowledged ? (
                      <>
                        <CheckCircle className="w-5 h-5 text-green-600" />
                        You're Responding
                      </>
                    ) : (
                      <>
                        <Navigation className="w-5 h-5" />
                        I'm Coming to Help
                      </>
                    )}
                  </button>

                  {alert.has_acknowledged && (
                    <button
                      onClick={() => handleNavigateToSOS(alert)}
                      className="w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3 px-4 rounded-xl flex items-center justify-center gap-2 transition-colors text-sm shadow-sm"
                    >
                      <Navigation className="w-5 h-5" />
                      Navigate to SOS
                    </button>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

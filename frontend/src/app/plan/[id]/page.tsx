"use client";

import { useEffect, useState, useMemo, useCallback } from "react"
import { useParams } from "next/navigation"
import {
  GoogleMap,
  useJsApiLoader,
  MarkerF,
} from '@react-google-maps/api';
import {
  Loader2,
  MapPinIcon,
  ImageIcon,
  CalendarDays,
  Info,
  BedDouble,
  Utensils,
  MountainSnow,
  Landmark,
  Ticket,
  ShoppingBag,
  ClockIcon,
  Map as MapIconLucide,
  ClipboardList,
  Navigation,
  AlertTriangle,
  PlayCircle,
} from "lucide-react"
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion"

// --- INTERFACES (no changes) ---
interface ActivityLocation {
  name: string | null;
  lat: number | null;
  lng: number | null;
}

interface Activity {
  time: string | null;
  title: string | null;
  description: string | null;
  type: string | null;
  map_link: string | null;
  location: ActivityLocation;
  photo_url?: string;
  place_id?: string;
}

interface Accommodation {
  hotel_name: string | null;
  check_in: string | null;
  address: string | null;
}

interface DailyPlan {
  day: number | null;
  date: string | null;
  city: string | null;
  summary: string | null;
  accommodation: Accommodation | null;
  activities: Activity[];
  notes: string | null;
}

interface MapLocation {
  name: string | null;
  lat: number | null;
  lng: number | null;
  day?: number | null;
  type?: string | null;
}

interface MapLocationForMapComponent {
  name: string | null;
  lat: number;
  lng: number;
  day?: number | null;
  type?: string | null;
}

interface MapSummary {
  locations: MapLocation[];
}

interface GeneratedPlan {
  trip_name: string | null;
  start_date: string | null;
  end_date: string | null;
  duration_days: number | null;
  destination_country: string | null;
  destination_cities: string[];
  daily_plan: DailyPlan[];
  map_summary: MapSummary | null;
  general_notes: string[] | null;
}

// --- MAP COMPONENT (TripMapComponent - MODIFIED MARKER KEY) ---
const mapContainerStyle = {
  width: '100%',
  height: '450px',
  borderRadius: '0.5rem',
};

interface TripMapComponentProps {
  locations: MapLocationForMapComponent[];
  apiKey: string;
  selectedLocation: MapLocationForMapComponent | null;
}

function TripMapComponent({ locations, apiKey, selectedLocation }: TripMapComponentProps) {
  const { isLoaded, loadError } = useJsApiLoader({
    id: 'google-map-script',
    googleMapsApiKey: apiKey,
  });

  const [mapRef, setMapRef] = useState<google.maps.Map | null>(null);

  const onLoad = useCallback((mapInstance: google.maps.Map) => {
    setMapRef(mapInstance);
    if (locations.length > 0) {
      const newBounds = new window.google.maps.LatLngBounds();
      locations.forEach(loc => {
        if (loc.lat != null && loc.lng != null) {
             newBounds.extend(new window.google.maps.LatLng(loc.lat, loc.lng));
        }
      });
      if (!newBounds.isEmpty()){
        mapInstance.fitBounds(newBounds);
        if (locations.length === 1) {
            const listener = window.google.maps.event.addListener(mapInstance, 'idle', () => {
            if (mapInstance.getZoom()! > 14) mapInstance.setZoom(14);
            window.google.maps.event.removeListener(listener);
            });
        }
      }
    }
  }, [locations]);

  const onUnmount = useCallback(() => {
    setMapRef(null);
  }, []);

  useEffect(() => {
    if (mapRef && selectedLocation && selectedLocation.lat != null && selectedLocation.lng != null) {
      mapRef.panTo({ lat: selectedLocation.lat, lng: selectedLocation.lng });
      mapRef.setZoom(15);
    }
  }, [mapRef, selectedLocation]);

  const mapOptions = useMemo(() => ({
    clickableIcons: false,
    streetViewControl: false,
    mapTypeControl: false,
    fullscreenControl: true,
    zoomControl: true,
  }), []);

  if (loadError) {
    console.error("Google Maps API load error:", loadError);
    return <div className="text-red-500 p-4 bg-red-100 rounded-md">Failed to load Google Maps. Check the console and API key configuration.</div>;
  }

  if (!isLoaded) {
    return (
      <div className="flex items-center justify-center" style={mapContainerStyle}>
        <Loader2 className="animate-spin w-8 h-8 text-blue-500" />
        <p className="ml-2 text-slate-600">Map loading...</p>
      </div>
    );
  }

  return (
    <GoogleMap
      mapContainerStyle={mapContainerStyle}
      options={mapOptions}
      onLoad={onLoad}
      onUnmount={onUnmount}
      center={locations.length > 0 && locations[0].lat != null && locations[0].lng != null ? { lat: locations[0].lat, lng: locations[0].lng } : { lat: 52.237049, lng: 21.017532 }}
      zoom={locations.length > 0 ? 6 : 5}
    >
      {locations.map((location, index) => ( // Added index
        location.lat != null && location.lng != null && (
            <MarkerF
            key={`${location.name || 'marker'}-${location.lat}-${location.lng}-${index}`} // MODIFIED KEY: Added index for uniqueness
            position={{ lat: location.lat, lng: location.lng }}
            title={location.name || 'Location'}
            />
        )
      ))}
    </GoogleMap>
  );
}

// --- HELPER FUNCTIONS ---
async function fetchWithRetries(
  url: string,
  options: RequestInit,
  maxRetries: number = 3,
  initialDelayMs: number = 1000
): Promise<any> {
  let lastError: any;
  for (let attempt = 0; attempt < maxRetries; attempt++) {
    try {
      const response = await fetch(url, options);
      if (!response.ok) {
        let errorBody;
        try { errorBody = await response.json(); } catch (e) { errorBody = { detail: response.statusText || `Server Error` }; }
        const errorMessage = typeof errorBody.detail === 'string' ? errorBody.detail : `Failed to fetch data (status: ${response.status})`;
        throw new Error(errorMessage);
      }
      const data = await response.json();
      return data;
    } catch (error) {
      lastError = error;
      if (attempt < maxRetries - 1) {
        const delay = initialDelayMs * Math.pow(2, attempt);
        await new Promise(resolve => setTimeout(resolve, delay));
      } else {
        throw new Error(`Failed to fetch plan after ${maxRetries} attempts. Last error: ${(lastError as Error).message}`);
      }
    }
  }
  throw lastError || new Error("Unknown error during data fetching after multiple attempts.");
}

// MODIFIED generateGoogleMapsLink function
const generateGoogleMapsLink = (activity: Activity): string => {
  const placeNameOrTitle = activity.location.name || activity.title || '';
  const encodedNameOrTitle = encodeURIComponent(placeNameOrTitle);

  // 1. Priority for existing, valid map_link (especially from Places API)
  if (activity.map_link && (activity.map_link.startsWith('http://') || activity.map_link.startsWith('https://'))) {
    // Simple check: if it's not one of the placeholder domains, assume it's OK
    if (!activity.map_link.includes('googleusercontent.com/maps.google.com/')) {
        return activity.map_link;
    }
  }

  // 2. Link using place_id (most reliable if available)
  if (activity.place_id) {
    return `https://www.google.com/maps/search/?api=1&query_place_id=$${activity.place_id}`;
  }

  // 3. Link using lat/lng
  if (activity.location.lat != null && activity.location.lng != null) {
    return `https://www.google.com/maps/@?api=1&map_action=map&center=$${activity.location.lat},${activity.location.lng}&zoom=17`;
  }

  // 4. Link using only name/title as query
  if (encodedNameOrTitle) {
    return `https://www.google.com/maps/search/?api=1&query=$${encodedNameOrTitle}`;
  }

  // 5. Fallback to generic Google Maps link if no other information
  return `https://www.google.com/maps`;
};


const getActivityIcon = (type: string | null) => {
  const typeLower = type?.toLowerCase() || ""
  // Polish keywords (obiad, kolacja, śniadanie, spacer, atrakcja, zabytek, wydarzenie, zakupy, nocleg)
  // are kept here as they are part of the logic based on expected input 'type' strings.
  // If these 'type' strings are also meant to be internationalized, that's a separate concern.
  if (typeLower.includes("eat") || typeLower.includes("food") || typeLower.includes("restaurant") || typeLower.includes("obiad") || typeLower.includes("kolacja") || typeLower.includes("śniadanie") || typeLower.includes("dinner") || typeLower.includes("lunch") || typeLower.includes("breakfast")) return <Utensils className="w-4 h-4 mr-1.5 text-orange-500 shrink-0" />;
  if (typeLower.includes("hike") || typeLower.includes("nature") || typeLower.includes("park") || typeLower.includes("spacer") || typeLower.includes("walk")) return <MountainSnow className="w-4 h-4 mr-1.5 text-green-500 shrink-0" />;
  if (typeLower.includes("museum") || typeLower.includes("landmark") || typeLower.includes("historical") || typeLower.includes("sightseeing") || typeLower.includes("atrakcja") || typeLower.includes("zabytek") || typeLower.includes("attraction")) return <Landmark className="w-4 h-4 mr-1.5 text-purple-500 shrink-0" />;
  if (typeLower.includes("tour") || typeLower.includes("event") || typeLower.includes("ticket") || typeLower.includes("wydarzenie")) return <Ticket className="w-4 h-4 mr-1.5 text-yellow-500 shrink-0" />;
  if (typeLower.includes("shop") || typeLower.includes("zakupy") || typeLower.includes("shopping")) return <ShoppingBag className="w-4 h-4 mr-1.5 text-pink-500 shrink-0" />;
  if (typeLower.includes("hotel") || typeLower.includes("sleep") || typeLower.includes("accommodation") || typeLower.includes("nocleg")) return <BedDouble className="w-4 h-4 mr-1.5 text-teal-500 shrink-0" />;
  return <Info className="w-4 h-4 mr-1.5 text-gray-500 shrink-0" />;
}


// --- MAIN PAGE COMPONENT ---
export default function PlanPage() {
  const params = useParams();
  const tripId = params?.id as string;

  const [generatedPlan, setGeneratedPlan] = useState<GeneratedPlan | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedMapLocation, setSelectedMapLocation] = useState<MapLocationForMapComponent | null>(null);
  const [isGenerationInitiated, setIsGenerationInitiated] = useState(false);

  const [displayName, setDisplayName] = useState<string | null>(null);
  const [displayNameLoading, setDisplayNameLoading] = useState<boolean>(true);

  const googleMapsApiKey = process.env.NEXT_PUBLIC_GOOGLE_PLACES_API_KEY;

  useEffect(() => {
    setDisplayNameLoading(true);
    if (tripId) {
      setTimeout(() => {
        const formattedName = tripId
          .split('-')
          .map(word => word.charAt(0).toUpperCase() + word.slice(1))
          .join(' ');
        setDisplayName(`Plan for: ${formattedName}`); // Changed "Plan dla:" to "Plan for:"
        setDisplayNameLoading(false);
      }, 300);
    } else {
      setDisplayName(null);
      setDisplayNameLoading(false);
    }
  }, [tripId]);


  const fetchPlanAndEnrich = useCallback(async () => {
    if (!tripId) {
        setError("Missing trip ID. Cannot continue."); // Translated
        setLoading(false);
        return;
    }
    setLoading(true);
    setError(null);
    console.log("Attempting to fetch and enrich plan for tripId:", tripId);

    try {
      let data: GeneratedPlan = await fetchWithRetries(
        `http://localhost:8001/generate-plan/${tripId}`,
        { method: "POST" }, 3, 1000
      );

      const apiKeyForPhotos = googleMapsApiKey; // Use the variable from the component scope
      console.log("Google Maps API Key for Photos:", apiKeyForPhotos ? "Available" : "NOT AVAILABLE");
      if (!apiKeyForPhotos) {
          console.warn("Google Places API key (NEXT_PUBLIC_GOOGLE_PLACES_API_KEY) is not configured. Photos from Google will not be fetched."); // Translated
      }

      if (data.daily_plan) {
        const enrichedDailyPlan = await Promise.all(
          data.daily_plan.map(async (day) => {
            if (!day.activities) return {...day, activities: []};

            const enrichedActivities = await Promise.all(
              day.activities.map(async (activity, activityIndex) => {
                let photoUrl = `https://source.unsplash.com/400x300/?${encodeURIComponent(activity.type || "travel")},${encodeURIComponent(activity.title || "destination")}&sig=${activityIndex}`; // sig for Unsplash uniqueness
                let placeId: string | undefined = activity.place_id;
                let finalMapLink = activity.map_link;

                const activityLogPrefix = `[Activity: "${activity.title || 'Untitled'}" Day: ${day.day}]`;
                console.log(`${activityLogPrefix} Initial: photo_url (fallback): ${photoUrl}, place_id: ${placeId}, map_link: ${activity.map_link}`);

                if (!apiKeyForPhotos) {
                    console.warn(`${activityLogPrefix} Skipping Google Places photo enrichment: API key missing.`);
                }

                // 1. Fetch Place ID if not available
                if (!placeId && activity.title && day.city && apiKeyForPhotos) {
                  const searchQuery = `${activity.title}, ${activity.location?.name || ''}, ${day.city}`;
                  console.log(`${activityLogPrefix} Finding place_id. Query: "${searchQuery}"`);
                  try {
                    const findPlaceResponse = await fetch('/api/google-places', {
                      method: 'POST', headers: { 'Content-Type': 'application/json' },
                      body: JSON.stringify({
                        operation: 'findplacefromtext', query: searchQuery, fields: 'place_id'
                      }),
                    });
                    const findPlaceData = await findPlaceResponse.json(); // Always parse JSON to get error details
                    if (findPlaceResponse.ok && findPlaceData.candidates && findPlaceData.candidates.length > 0) {
                      placeId = findPlaceData.candidates[0].place_id;
                      console.log(`${activityLogPrefix} Found place_id: ${placeId}`);
                    } else {
                      console.warn(`${activityLogPrefix} Failed to find place_id. Status: ${findPlaceResponse.status}. Response data:`, findPlaceData);
                      if (findPlaceData.error_message) console.warn(`${activityLogPrefix} Google API error (findplace): ${findPlaceData.error_message}`);
                    }
                  } catch (e) {
                    console.error(`${activityLogPrefix} Client error during findplacefromtext:`, e);
                  }
                } else if (placeId) {
                    console.log(`${activityLogPrefix} Using existing place_id: ${placeId}`);
                } else if (!activity.title || !day.city) {
                    console.log(`${activityLogPrefix} Skipping find place_id: title or city missing.`);
                }


                // 2. Fetch place details (including photos and URL) if Place ID is available
                if (placeId && apiKeyForPhotos) {
                   console.log(`${activityLogPrefix} PlaceID: ${placeId}. Getting place details.`);
                   try {
                      const placeDetailsResponse = await fetch('/api/google-places', {
                          method: 'POST', headers: { 'Content-Type': 'application/json' },
                          body: JSON.stringify({ operation: 'details', placeId: placeId, fields: 'photos,url,name' }),
                      });
                      const placeDetailsData = await placeDetailsResponse.json(); // Always parse JSON
                      if (placeDetailsResponse.ok && placeDetailsData.result) {
                          console.log(`${activityLogPrefix} PlaceID: ${placeId}. Received place details:`, placeDetailsData.result);
                          if (placeDetailsData.result.photos && placeDetailsData.result.photos.length > 0) {
                              const photoReference = placeDetailsData.result.photos[0].photo_reference;
                              photoUrl = `https://maps.googleapis.com/maps/api/place/photo?maxwidth=400&photoreference=${photoReference}&key=${apiKeyForPhotos}`;
                              console.log(`${activityLogPrefix} PlaceID: ${placeId}. Constructed Google Photo URL: ${photoUrl}`);
                          } else {
                              console.log(`${activityLogPrefix} PlaceID: ${placeId}. No photos found in place details. Using fallback: ${photoUrl}`);
                          }
                          // Use Google's URL for the map link if a better one isn't available
                          if (placeDetailsData.result.url && (!finalMapLink || finalMapLink.includes('googleusercontent.com'))) {
                             finalMapLink = placeDetailsData.result.url;
                             console.log(`${activityLogPrefix} PlaceID: ${placeId}. Using Google Maps URL from details: ${finalMapLink}`);
                          }
                      } else {
                         console.warn(`${activityLogPrefix} PlaceID: ${placeId}. Failed to get place details. Status: ${placeDetailsResponse.status}. Response data:`, placeDetailsData);
                         if (placeDetailsData.error_message) console.warn(`${activityLogPrefix} Google API error (details): ${placeDetailsData.error_message}`);
                      }
                   } catch (e) {
                     console.error(`${activityLogPrefix} PlaceID: ${placeId}. Client error during place details fetch:`, e);
                   }
                } else if (!placeId && apiKeyForPhotos) { // Only log if API key is present, but placeId is missing
                    console.log(`${activityLogPrefix} No place_id available, cannot fetch Google Place Details or Photos.`);
                }

                // If after all attempts finalMapLink is still invalid or empty, generate a new one
                if (!finalMapLink || finalMapLink.includes('googleusercontent.com')) {
                    const previouslyGeneratedLink = finalMapLink;
                    finalMapLink = generateGoogleMapsLink(activity); // Use the corrected function
                    if (previouslyGeneratedLink !== finalMapLink) {
                        console.log(`${activityLogPrefix} Generated new map link: ${finalMapLink} (was: ${previouslyGeneratedLink || 'empty'})`);
                    }
                }
                return { ...activity, photo_url: photoUrl, place_id: placeId, map_link: finalMapLink };
              })
            );
            return { ...day, activities: enrichedActivities };
          })
        );
        data = { ...data, daily_plan: enrichedDailyPlan };
      }
      setGeneratedPlan(data);
    } catch (err: any) {
      console.error("Final error after attempts to fetch plan:", err); // Translated
      setError(err.message || "Failed to generate plan after several attempts."); // Translated
      setGeneratedPlan(null);
    } finally {
      setLoading(false);
      console.log("Finished fetching and enriching plan.");
    }
  }, [tripId, googleMapsApiKey]); // googleMapsApiKey added as dependency

  const handleGeneratePlanClick = () => {
    if (!tripId) {
      setError("No trip ID in URL. Cannot generate plan."); // Translated
      return;
    }
    if (displayNameLoading) {
        setError("Please wait for trip details to load."); // Translated
        return;
    }
    setError(null);
    setIsGenerationInitiated(true);
    fetchPlanAndEnrich();
  };
  
  const validMapLocations = useMemo((): MapLocationForMapComponent[] => {
    if (!generatedPlan?.map_summary?.locations) return [];
    return generatedPlan.map_summary.locations
      .filter(loc => loc.lat != null && loc.lng != null && !isNaN(loc.lat) && !isNaN(loc.lng))
      .map(loc => ({
        name: loc.name,
        lat: loc.lat as number,
        lng: loc.lng as number,
        day: loc.day,
        type: loc.type,
      }));
  }, [generatedPlan?.map_summary?.locations]);

  // --- RENDERING (rest unchanged, unless further modifications are needed) ---

  if (!isGenerationInitiated) {
    return (
      <div className="flex flex-col items-center justify-center min-h-screen p-4 bg-gradient-to-br from-slate-100 via-sky-50 to-slate-100 text-center">
        <div className="bg-white p-6 md:p-10 rounded-xl shadow-2xl max-w-md w-full">
          <PlayCircle className="w-12 h-12 text-blue-500 mx-auto mb-4" />
          <h1 className="text-2xl md:text-3xl font-semibold text-slate-700 mb-3">
            Your Travel Plan is waiting!
          </h1>
          <p className="text-slate-500 mb-5 text-sm">
            Click the button below to start generating your schedule.
          </p>

          {displayNameLoading && (
            <div className="my-3 h-5 flex items-center justify-center">
              <Loader2 className="animate-spin w-4 h-4 text-slate-400" />
              <p className="text-xs text-slate-400 ml-2">Loading...</p>
            </div>
          )}
          {!displayNameLoading && displayName && (
            <p className="text-sm text-slate-600 mb-5 font-medium">
               <span className="text-slate-500">For:</span> <strong className="text-blue-600">{displayName.replace("Plan for: ", "")}</strong> {/* Changed "Plan dla:" */}
            </p>
          )}
           {!displayNameLoading && !displayName && tripId && (
            <p className="text-xs text-slate-400 mb-5">
                Travel ID: {tripId}
            </p>
          )}

          <button
            onClick={handleGeneratePlanClick}
            disabled={!tripId || displayNameLoading || loading}
            className="w-full px-6 py-3 bg-blue-500 text-white rounded-lg text-base font-medium hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-400 focus:ring-opacity-50 transition-all duration-200 ease-in-out transform hover:scale-105 disabled:bg-slate-300 disabled:text-slate-500 disabled:cursor-not-allowed disabled:transform-none"
          >
            {loading ? (
              <Loader2 className="animate-spin w-5 h-5 mx-auto" />
            ) : (
              "Generate Plan" // Translated
            )}
          </button>

          {(!tripId && !error) && (
            <div className="mt-3 text-orange-600 bg-orange-50 p-2.5 rounded-md shadow-sm text-xs">
              <AlertTriangle className="inline-block w-3.5 h-3.5 mr-1.5 relative -top-px" />
              No trip ID detected. The plan cannot be generated. {/* Translated */}
            </div>
          )}
          {error && (
             <div className="mt-3 text-red-600 bg-red-50 p-2.5 rounded-md shadow-sm text-xs">
                <AlertTriangle className="inline-block w-3.5 h-3.5 mr-1.5 relative -top-px" />
                {error}
            </div>
          )}
        </div>
      </div>
    );
  }

  if (loading) { 
    return (
      <div className="flex flex-col items-center justify-center min-h-screen p-6 bg-slate-50">
        <Loader2 className="animate-spin w-12 h-12 text-blue-600 mb-4" />
        <p className="text-lg text-slate-700">Generating Your travel plan...</p>
        <p className="text-sm text-slate-500">This may take a moment, we're loading the magic!</p>
      </div>
    );
  }

  if (error) { 
    return (
      <div className="flex flex-col items-center justify-center min-h-screen p-6 bg-red-50 text-red-700">
        <AlertTriangle className="w-12 h-12 mb-4 text-red-500" />
        <h2 className="text-2xl font-semibold mb-2">Error</h2>
        <p className="text-center max-w-md mb-6">{error}</p>
        <button 
            onClick={handleGeneratePlanClick}
            disabled={!tripId || displayNameLoading || loading}
            className="px-6 py-3 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors disabled:bg-slate-400 disabled:cursor-not-allowed mb-2"
        >
            {loading ? <Loader2 className="animate-spin w-5 h-5 mx-auto" /> : "Try generating again"} {/* Translated */}
        </button>
        <button 
            onClick={() => { setIsGenerationInitiated(false); setError(null); setGeneratedPlan(null); }} 
            className="px-6 py-3 bg-slate-200 text-slate-700 rounded-lg hover:bg-slate-300 transition-colors"
        >
            Back {/* Translated */}
        </button>
      </div>
    );
  }

  if (!generatedPlan) { 
    return (
        <div className="flex flex-col items-center justify-center min-h-screen p-6 bg-slate-50">
            <Info className="w-12 h-12 text-slate-500 mb-4" />
            <p className="text-lg text-slate-700 mb-6">Travel plan not found or an unexpected problem occurred.</p> {/* Translated */}
            <button 
                onClick={handleGeneratePlanClick}
                disabled={!tripId || displayNameLoading || loading}
                className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:bg-slate-400 disabled:cursor-not-allowed mb-2"
            >
                {loading ? <Loader2 className="animate-spin w-5 h-5 mx-auto" /> : "Try again"} {/* Translated */}
            </button>
            <button 
                onClick={() => { setIsGenerationInitiated(false); setError(null); }} 
                className="px-6 py-3 bg-slate-200 text-slate-700 rounded-lg hover:bg-slate-300 transition-colors"
            >
                Back {/* Translated */}
            </button>
        </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-100 via-sky-50 to-slate-100 py-8 md:py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-5xl mx-auto space-y-8">
        <header className="text-center mb-8 md:mb-12">
          <h1 className="text-4xl md:text-5xl font-bold text-slate-800 mb-2">
            {generatedPlan.trip_name || "Your Travel Plan"} {/* Translated */}
          </h1>
          {generatedPlan.destination_country && (
            <p className="text-xl text-slate-600">
              {(generatedPlan.destination_cities || []).join(", ")} • {generatedPlan.destination_country}
            </p>
          )}
           {generatedPlan.start_date && generatedPlan.end_date && (
            <p className="text-md text-slate-500 mt-1">
                <CalendarDays className="inline-block w-4 h-4 mr-1.5 relative -top-px" />
                {generatedPlan.start_date} – {generatedPlan.end_date} ({generatedPlan.duration_days || 'N/A'} days) {/* Translated "dni" */}
            </p>
           )}
        </header>
        
        <section className="bg-white p-6 rounded-xl shadow-lg">
          <div className="flex items-center mb-4">
            <CalendarDays className="w-7 h-7 mr-3 text-blue-600" />
            <h2 className="text-2xl md:text-3xl font-semibold text-slate-800">Daily Plan</h2> {/* Translated */}
          </div>
          {generatedPlan.daily_plan && generatedPlan.daily_plan.length > 0 ? (
            <Accordion type="single" collapsible defaultValue={`day-0`}>
              {generatedPlan.daily_plan.map((day, idx) => {
                if (!day) return null; 
                const dayNumber = day.day !== null && day.day !== undefined ? day.day : idx + 1;
                return (
                <AccordionItem key={idx} value={`day-${idx}`} className="border-b border-slate-200 last:border-b-0">
                  <AccordionTrigger className="text-xl font-medium hover:bg-slate-50 data-[state=open]:bg-sky-50 px-4 py-4 rounded-lg transition-colors duration-150 w-full text-left">
                    <div className="flex items-center justify-between w-full">
                        <div className="flex items-center">
                            <span className="text-sm font-semibold bg-blue-500 text-white rounded-full w-7 h-7 flex items-center justify-center mr-3 shrink-0">
                                {dayNumber}
                            </span>
                            <span className="text-slate-700">{day.city || 'Unknown city'} <span className="text-slate-500 font-normal text-base">({day.date || 'No date'})</span></span> {/* Translated */}
                        </div>
                    </div>
                  </AccordionTrigger>
                  <AccordionContent className="pt-4 pb-6 px-4 bg-slate-50/50 rounded-b-lg">
                    {day.summary && <p className="mb-4 text-slate-700 italic">"{day.summary}"</p>}
                    {day.accommodation && day.accommodation.hotel_name && (
                       <div className="mb-6 p-4 bg-sky-50 rounded-lg border border-sky-200">
                            <h3 className="font-semibold text-lg text-sky-800 mb-2 flex items-center">
                                <BedDouble className="w-5 h-5 mr-2 text-sky-600" /> Accommodation {/* Translated */}
                            </h3>
                            <p className="text-slate-700"><strong>{day.accommodation.hotel_name}</strong></p>
                            {day.accommodation.address && <p className="text-sm text-slate-600">{day.accommodation.address}</p>}
                            {day.accommodation.check_in && <p className="text-sm text-slate-500">Check-in: {day.accommodation.check_in}</p>} {/* Translated */}
                        </div>
                    )}

                    {day.activities && day.activities.length > 0 && (
                      <>
                        <h3 className="font-semibold text-lg text-slate-700 mt-4 mb-3">Attractions and Activities:</h3> {/* Translated */}
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                          {day.activities.map((activity, i) => {
                            if (!activity) return null; 
                            const mapLink = activity.map_link || generateGoogleMapsLink(activity); // Use link from activity or generate
                            return (
                              <a key={i} href={mapLink} target="_blank" rel="noopener noreferrer"
                                className="block bg-white rounded-lg shadow-md hover:shadow-xl transition-all duration-300 overflow-hidden group">
                                {activity.photo_url ? (
                                  <div className="relative h-48 w-full overflow-hidden">
                                    <img src={activity.photo_url} alt={activity.title || 'Attraction photo'} /* Translated */
                                      className="w-full h-full object-cover transition-transform duration-300 group-hover:scale-105"
                                      onError={(e) => {
                                        console.warn(`[Image Error] Failed to load: ${activity.photo_url}. Falling back to Unsplash for "${activity.title}"`);
                                        (e.target as HTMLImageElement).src = `https://source.unsplash.com/400x300/?travel,${encodeURIComponent(activity.location?.name || activity.title || 'placeholder')}`;
                                      }} />
                                  </div>
                                ) : ( <div className="w-full h-48 bg-slate-200 flex items-center justify-center"><ImageIcon className="w-12 h-12 text-slate-400" /></div> )}
                                <div className="p-4">
                                  <h4 className="font-semibold text-lg text-slate-800 mb-1 group-hover:text-blue-600 transition-colors duration-200">{activity.title || 'No title'}</h4> {/* Translated */}
                                  <div className="text-sm text-slate-500 mb-2 space-y-0.5">
                                    {activity.time && ( <p className="flex items-center"><ClockIcon className="w-4 h-4 mr-1.5 text-blue-500 shrink-0" /> {activity.time}</p> )}
                                    {activity.type && ( <p className="flex items-center">{getActivityIcon(activity.type)} {activity.type}</p> )}
                                  </div>
                                  {activity.description && <p className="mb-2 text-sm text-slate-600 leading-relaxed line-clamp-3">{activity.description}</p>}
                                  {activity.location?.name && ( <p className="text-sm text-slate-600 flex items-center mt-1"><MapPinIcon className="w-4 h-4 mr-1.5 text-red-500 shrink-0" /> {activity.location.name}</p> )}
                                   <span className="inline-flex items-center mt-3 text-sm text-blue-600 group-hover:underline">
                                    View on map <Navigation className="w-3.5 h-3.5 ml-1" /> {/* Translated */}
                                  </span>
                                </div>
                              </a>
                            );
                          })}
                        </div>
                      </>
                    )}
                    {day.notes && (
                        <div className="mt-6 p-3 bg-amber-50 border border-amber-200 rounded-md">
                            <h4 className="font-semibold text-md text-amber-800 mb-1">Notes for the day:</h4> {/* Translated */}
                            <p className="text-sm text-amber-700 whitespace-pre-line">{day.notes}</p>
                        </div>
                    )}
                    {(!day.activities || day.activities.length === 0) && !day.accommodation?.hotel_name && !day.notes && ( <p className="text-slate-500">No planned activities, accommodation, or notes for this day.</p> )} {/* Translated */}
                  </AccordionContent>
                </AccordionItem>
                );
            })}
            </Accordion>
          ) : ( <p className="text-slate-500 text-center py-4">No detailed plan for individual days.</p> )} {/* Translated */}
        </section>

        <section className="bg-white p-6 rounded-xl shadow-lg">
            <div className="flex items-center mb-6">
              <MapIconLucide className="w-7 h-7 mr-3 text-green-600" />
              <h2 className="text-2xl md:text-3xl font-semibold text-slate-800">Trip Map</h2> {/* Translated */}
            </div>
            {googleMapsApiKey && validMapLocations.length > 0 ? (
              <TripMapComponent 
                locations={validMapLocations} 
                apiKey={googleMapsApiKey}
                selectedLocation={selectedMapLocation}
              />
            ) : (
              <div className="p-4 bg-slate-100 rounded-md text-center">
                <p className="text-slate-600">
                  {validMapLocations.length === 0 && generatedPlan?.map_summary?.locations && generatedPlan.map_summary.locations.length > 0 
                    ? "Some locations do not have valid coordinates and cannot be displayed on the map." // Translated
                    : "No locations to display on the map." // Translated
                  }
                  {!googleMapsApiKey && " Google Maps API key is not configured, the map cannot be displayed."} {/* Translated */}
                </p>
              </div>
            )}
            
            {validMapLocations.length > 0 && (
              <div className="mt-6">
                <h3 className="text-lg font-semibold text-slate-700 mb-3">List of key locations:</h3> {/* Translated */}
                <ul className="space-y-1 text-sm max-h-60 overflow-y-auto pr-2">
                  {validMapLocations.map((loc, idx) => (
                    <li 
                      key={idx} 
                      className={`flex items-center text-slate-700 p-2.5 hover:bg-sky-50 rounded-md cursor-pointer transition-colors duration-150 ${selectedMapLocation === loc ? 'bg-sky-100' : ''}`}
                      onClick={() => setSelectedMapLocation(loc)}
                    >
                      <MapPinIcon className={`w-5 h-5 mr-2.5 shrink-0 ${selectedMapLocation === loc ? 'text-blue-600 scale-110' : 'text-red-500'}`} />
                      <span className={`font-medium ${selectedMapLocation === loc ? 'text-blue-600' : ''}`}>{loc.name || "Unknown location"}</span> {/* Translated */}
                      {loc.day && <span className="text-xs text-slate-400 ml-2">(Day {loc.day})</span>} {/* Translated "Dzień" */}
                      {loc.type && <span className="ml-auto text-xs bg-green-100 text-green-700 px-2 py-0.5 rounded-full font-medium">{loc.type}</span>}
                    </li>
                  ))}
                </ul>
              </div>
            )}
        </section>

        {generatedPlan.general_notes && generatedPlan.general_notes.length > 0 && (
          <section className="bg-white p-6 rounded-xl shadow-lg">
             <div className="flex items-center mb-4"> <ClipboardList className="w-7 h-7 mr-3 text-purple-600" />
                <h2 className="text-2xl md:text-3xl font-semibold text-slate-800">General Notes</h2> {/* Translated */}
            </div>
            <ul className="list-disc ml-5 space-y-1 text-slate-700">
              {generatedPlan.general_notes.map((note, idx) => ( <li key={idx}>{note}</li> ))}
            </ul>
          </section>
        )}
      </div>
      <footer className="text-center mt-12 py-6 border-t border-slate-200">
        <p className="text-sm text-slate-500">Travel plan generated. Have a great adventure!</p> {/* Translated */}
      </footer>
    </div>
  );
};
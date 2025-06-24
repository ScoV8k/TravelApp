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

interface Activity {
  place_id: string | null;
  time: string | null;
  title: string | null;
  description: string | null;
  type: string | null;
  lat: number | null;
  lng: number | null;
  location_name: string | null;
  maps_url: string | null;
  // photo_url?: string | null;
  photo_reference?: string | null;
  tags?: string[];
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

interface GeneratedPlan {
  trip_name: string | null;
  start_date: string | null;
  end_date: string | null;
  duration_days: number | null;
  destination_country: string | null;
  destination_cities: string[];
  daily_plan: DailyPlan[];
  general_notes: string[] | null;
}

interface MapLocationForMapComponent {
  name: string | null;
  lat: number;
  lng: number;
  day?: number | null;
  type?: string | null;
}


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
        const zoom = mapInstance.getZoom() ?? 0;
        if (zoom > 15) {
            mapInstance.setZoom(15);
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
    return <div className="text-red-500 p-4 bg-red-100 rounded-md">Nie udało się załadować map Google.</div>;
  }

  if (!isLoaded) {
    return (
      <div className="flex items-center justify-center" style={mapContainerStyle}>
        <Loader2 className="animate-spin w-8 h-8 text-blue-500" />
        <p className="ml-2 text-slate-600">Ładowanie mapy...</p>
      </div>
    );
  }

  return (
    <GoogleMap
      mapContainerStyle={mapContainerStyle}
      options={mapOptions}
      onLoad={onLoad}
      onUnmount={onUnmount}
    >
      {locations.map((location, index) => (
        location.lat != null && location.lng != null && (
            <MarkerF
            key={`${location.name || 'marker'}-${location.lat}-${location.lng}-${index}`}
            position={{ lat: location.lat, lng: location.lng }}
            title={location.name || 'Location'}
            />
        )
      ))}
    </GoogleMap>
  );
}

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
                try { errorBody = await response.json(); } catch (e) { errorBody = { detail: response.statusText || `Błąd serwera` }; }
                const errorMessage = typeof errorBody.detail === 'string' ? errorBody.detail : `Błąd pobierania danych (status: ${response.status})`;
                throw new Error(errorMessage);
            }
            return await response.json();
        } catch (error) {
            lastError = error;
            if (attempt < maxRetries - 1) {
                const delay = initialDelayMs * Math.pow(2, attempt);
                await new Promise(resolve => setTimeout(resolve, delay));
            } else {
                throw new Error(`Nie udało się pobrać planu po ${maxRetries} próbach. Ostatni błąd: ${(lastError as Error).message}`);
            }
        }
    }
    throw lastError || new Error("Nieznany błąd podczas pobierania danych po wielu próbach.");
}


const getActivityIcon = (type: string | null) => {
  const typeLower = type?.toLowerCase() || ""
  if (typeLower.includes("eat") || typeLower.includes("food") || typeLower.includes("restaurant") || typeLower.includes("obiad") || typeLower.includes("kolacja") || typeLower.includes("śniadanie") || typeLower.includes("dinner") || typeLower.includes("lunch") || typeLower.includes("breakfast")) return <Utensils className="w-4 h-4 mr-1.5 text-orange-500 shrink-0" />;
  if (typeLower.includes("hike") || typeLower.includes("nature") || typeLower.includes("park") || typeLower.includes("spacer") || typeLower.includes("walk")) return <MountainSnow className="w-4 h-4 mr-1.5 text-green-500 shrink-0" />;
  if (typeLower.includes("museum") || typeLower.includes("landmark") || typeLower.includes("historical") || typeLower.includes("sightseeing") || typeLower.includes("atrakcja") || typeLower.includes("zabytek") || typeLower.includes("attraction")) return <Landmark className="w-4 h-4 mr-1.5 text-purple-500 shrink-0" />;
  if (typeLower.includes("tour") || typeLower.includes("event") || typeLower.includes("ticket") || typeLower.includes("wydarzenie")) return <Ticket className="w-4 h-4 mr-1.5 text-yellow-500 shrink-0" />;
  if (typeLower.includes("shop") || typeLower.includes("zakupy") || typeLower.includes("shopping")) return <ShoppingBag className="w-4 h-4 mr-1.5 text-pink-500 shrink-0" />;
  if (typeLower.includes("hotel") || typeLower.includes("sleep") || typeLower.includes("accommodation") || typeLower.includes("nocleg")) return <BedDouble className="w-4 h-4 mr-1.5 text-teal-500 shrink-0" />;
  return <Info className="w-4 h-4 mr-1.5 text-gray-500 shrink-0" />;
}


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
  const [isSaving, setIsSaving] = useState(false);
  const [saveMessage, setSaveMessage] = useState<string | null>(null);
  const [tripStatus, setTripStatus] = useState<"draft" | "planned" | null>(null);

  useEffect(() => {
    const checkTripStatus = async () => {
      if (!tripId) return;
      try {
        const res = await fetch(`http://localhost:8000/trips/status/${tripId}`);
        if (!res.ok) throw new Error("Nie udało się pobrać statusu podróży");
        const data = await res.json();
        console.log(res);
        setTripStatus(data.status);
        if (data.status === "planned") {
          const planRes = await fetch(`http://localhost:8000/plans/${tripId}`);
          if (!planRes.ok) throw new Error("Nie udało się pobrać planu podróży");
          const planData = await planRes.json();
          setGeneratedPlan(planData.data);
          console.log("SIEMAAAAAA: ", planData.data);
        }
      } catch (err: any) {
        console.error(err);
        setError(err.message || "Błąd pobierania statusu lub planu");
      }
    };
    checkTripStatus();
  }, [tripId]);

  const googleMapsApiKey = process.env.NEXT_PUBLIC_GOOGLE_PLACES_API_KEY;

  useEffect(() => {
    setDisplayNameLoading(true);
    if (tripId) {
      setTimeout(() => {
        const formattedName = tripId
          .split('-')
          .map(word => word.charAt(0).toUpperCase() + word.slice(1))
          .join(' ');
        setDisplayName(`Plan dla: ${formattedName}`);
        setDisplayNameLoading(false);
      }, 300);
    } else {
      setDisplayName(null);
      setDisplayNameLoading(false);
    }
  }, [tripId]);
  
  const fetchPlan = useCallback(async () => {
  if (!tripId) {
    setError("Brak ID podróży. Nie można kontynuować.");
    setLoading(false);
    return;
  }
  setLoading(true);
  setError(null);

  try {
    const fullResponse = await fetchWithRetries(
      `http://localhost:8001/generate-plan/${tripId}`,
      { method: "POST" }
    );

    const plan: GeneratedPlan = fullResponse.data;

    setGeneratedPlan(plan);

  } catch (err: any) {
    setError(err.message || "Nie udało się wygenerować planu po kilku próbach.");
    setGeneratedPlan(null);
  } finally {
    setLoading(false);
  }
}, [tripId]);


  const handleGeneratePlanClick = () => {
      if (!tripId) {
          setError("Brak ID podróży w URL. Nie można wygenerować planu.");
          return;
      }
      setError(null);
      setIsGenerationInitiated(true);
      fetchPlan();
  };
  
  const validMapLocations = useMemo((): MapLocationForMapComponent[] => {
      if (!generatedPlan?.daily_plan) return [];
      
      const locations: MapLocationForMapComponent[] = [];
      
      generatedPlan.daily_plan.forEach(day => {
          day.activities?.forEach(activity => {
              if (activity.lat != null && activity.lng != null && !isNaN(activity.lat) && !isNaN(activity.lng)) {
                  locations.push({
                      name: activity.location_name || activity.title,
                      lat: activity.lat,
                      lng: activity.lng,
                      day: day.day,
                      type: activity.type,
                  });
              }
          });
      });
      
      return locations;
  }, [generatedPlan?.daily_plan]);

  useEffect(() => {
  console.log("📍 MAP LOCATIONS", validMapLocations);
}, [validMapLocations]);

  if (tripStatus === null) {
  return (
    <div className="flex flex-col items-center justify-center min-h-screen p-6 bg-slate-50">
      <Loader2 className="animate-spin w-12 h-12 text-blue-600 mb-4" />
      <p className="text-lg text-slate-700">Sprawdzanie statusu podróży...</p>
    </div>
  );
}

  if (tripStatus === "draft" && !isGenerationInitiated) {
    return (
      <div className="flex flex-col items-center justify-center min-h-screen p-4 bg-gradient-to-br from-slate-100 via-sky-50 to-slate-100 text-center">
        <div className="bg-white p-6 md:p-10 rounded-xl shadow-2xl max-w-md w-full">
          <PlayCircle className="w-12 h-12 text-blue-500 mx-auto mb-4" />
          <h1 className="text-2xl md:text-3xl font-semibold text-slate-700 mb-3">
            Twój plan podróży czeka!
          </h1>
          <p className="text-slate-500 mb-5 text-sm">
            Kliknij przycisk poniżej, aby rozpocząć generowanie harmonogramu.
          </p>

          {displayNameLoading && (
            <div className="my-3 h-5 flex items-center justify-center">
              <Loader2 className="animate-spin w-4 h-4 text-slate-400" />
              <p className="text-xs text-slate-400 ml-2">Ładowanie...</p>
            </div>
          )}
          {!displayNameLoading && displayName && (
            <p className="text-sm text-slate-600 mb-5 font-medium">
               <span className="text-slate-500">Dla:</span> <strong className="text-blue-600">{displayName.replace("Plan dla: ", "")}</strong>
            </p>
          )}

          <button
            onClick={handleGeneratePlanClick}
            disabled={!tripId || displayNameLoading || loading}
            className="w-full px-6 py-3 bg-blue-500 text-white rounded-lg text-base font-medium hover:bg-blue-600 disabled:bg-slate-300 disabled:cursor-not-allowed"
          >
            {loading ? <Loader2 className="animate-spin w-5 h-5 mx-auto" /> : "Generuj Plan"}
          </button>

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
        <p className="text-lg text-slate-700">Generowanie Twojego planu podróży...</p>
      </div>
    );
  }

  if (error) { 
    return (
      <div className="flex flex-col items-center justify-center min-h-screen p-6 bg-red-50 text-red-700">
        <AlertTriangle className="w-12 h-12 mb-4 text-red-500" />
        <h2 className="text-2xl font-semibold mb-2">Błąd</h2>
        <p className="text-center max-w-md mb-6">{error}</p>
        <button 
            onClick={handleGeneratePlanClick}
            className="px-6 py-3 bg-red-600 text-white rounded-lg hover:bg-red-700"
        >
            Spróbuj wygenerować ponownie
        </button>
      </div>
    );
  }

  if (!generatedPlan) { 
    return (
      <div className="flex flex-col items-center justify-center min-h-screen p-6 bg-slate-50">
          <Info className="w-12 h-12 text-slate-500 mb-4" />
          <p className="text-lg text-slate-700">Nie znaleziono planu podróży.</p>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-100 via-sky-50 to-slate-100 py-8 md:py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-5xl mx-auto space-y-8">
        <header className="text-center mb-8 md:mb-12">
          <h1 className="text-4xl md:text-5xl font-bold text-slate-800 mb-2">
            {generatedPlan.trip_name || "Twój Plan Podróży"}
          </h1>
          {generatedPlan.destination_country && (
            <p className="text-xl text-slate-600">
              {(generatedPlan.destination_cities || []).join(", ")} • {generatedPlan.destination_country}
            </p>
          )}
           {generatedPlan.start_date && generatedPlan.end_date && (
            <p className="text-md text-slate-500 mt-1">
                <CalendarDays className="inline-block w-4 h-4 mr-1.5 relative -top-px" />
                {generatedPlan.start_date} – {generatedPlan.end_date} ({generatedPlan.duration_days || 'N/A'} dni)
            </p>
           )}
        </header>
        
        <section className="bg-white p-6 rounded-xl shadow-lg">
          <div className="flex items-center mb-4">
            <CalendarDays className="w-7 h-7 mr-3 text-blue-600" />
            <h2 className="text-2xl md:text-3xl font-semibold text-slate-800">Plan Dnia</h2>
          </div>
          {generatedPlan.daily_plan && generatedPlan.daily_plan.length > 0 ? (
            <Accordion type="single" collapsible defaultValue={`day-0`}>
              {generatedPlan.daily_plan.map((day, idx) => (
                <AccordionItem key={idx} value={`day-${idx}`} className="border-b border-slate-200 last:border-b-0">
                  <AccordionTrigger className="text-xl font-medium hover:bg-slate-50 data-[state=open]:bg-sky-50 px-4 py-4 rounded-lg">
                    <div className="flex items-center">
                        <span className="text-sm font-semibold bg-blue-500 text-white rounded-full w-7 h-7 flex items-center justify-center mr-3 shrink-0">
                            {day.day}
                        </span>
                        <span className="text-slate-700">{day.city} <span className="text-slate-500 font-normal text-base">({day.date})</span></span>
                    </div>
                  </AccordionTrigger>
                  <AccordionContent className="pt-4 pb-6 px-4 bg-slate-50/50 rounded-b-lg">
                    {day.summary && <p className="mb-4 text-slate-700 italic">"{day.summary}"</p>}
                    {day.accommodation && day.accommodation.hotel_name && (
                       <div className="mb-6 p-4 bg-sky-50 rounded-lg border border-sky-200">
                            <h3 className="font-semibold text-lg text-sky-800 mb-2 flex items-center">
                                <BedDouble className="w-5 h-5 mr-2 text-sky-600" /> Zakwaterowanie
                            </h3>
                            <p className="text-slate-700"><strong>{day.accommodation.hotel_name}</strong></p>
                            {day.accommodation.address && <p className="text-sm text-slate-600">{day.accommodation.address}</p>}
                            {day.accommodation.check_in && <p className="text-sm text-slate-500">Zameldowanie: {day.accommodation.check_in}</p>}
                        </div>
                    )}

                    {day.activities && day.activities.length > 0 && (
                      <>
                        <h3 className="font-semibold text-lg text-slate-700 mt-4 mb-3">Atrakcje i Aktywności:</h3>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                          {day.activities.map((activity, i) => {
                            if (!activity) return null; 
                            const mapLink = activity.maps_url || "abcd"
                            console.log(activity);
                            return (
                              <a key={i} href={mapLink} target="_blank" rel="noopener noreferrer"
                                className="block bg-white rounded-lg shadow-md hover:shadow-xl transition-all duration-300 overflow-hidden group">
                                {activity.photo_reference ? (
                                  <div className="relative h-48 w-full overflow-hidden">
                                    <img src={`http://localhost:8000/plans/proxy/photo?photoreference=${activity.photo_reference}`}
                                      className="w-full h-full object-cover transition-transform duration-300 group-hover:scale-105"
                                      onError={(e) => {
                                        console.warn(`[Image Error] Failed to load: ${activity.photo_reference}. Falling back to Unsplash for "${activity.title}"`);
                                        (e.target as HTMLImageElement).src = `https://source.unsplash.com/400x300/?travel,${encodeURIComponent(activity.location_name || activity.title || 'placeholder')}`;
                                      }} />
                                  </div>
                                ) : (
                                  <div className="w-full h-48 bg-slate-200 flex items-center justify-center">
                                      <ImageIcon className="w-12 h-12 text-slate-400" />
                                  </div>
                                )}


                                <div className="p-4">
                                    <h4 className="font-semibold text-lg text-slate-800 mb-1 group-hover:text-blue-600">{activity.title}</h4>
                                    <div className="text-sm text-slate-500 mb-2 space-y-0.5">
                                        {activity.time && (<p className="flex items-center"><ClockIcon className="w-4 h-4 mr-1.5 text-blue-500" /> {activity.time}</p>)}
                                        {activity.type && (<p className="flex items-center">{getActivityIcon(activity.type)} {activity.type}</p>)}
                                    </div>
                                    {activity.description && <p className="mb-2 text-sm text-slate-600 line-clamp-3">{activity.description}</p>}
                                    {activity.location_name && (<p className="text-sm text-slate-600 flex items-center mt-1"><MapPinIcon className="w-4 h-4 mr-1.5 text-red-500" /> {activity.location_name}</p>)}
                                    <span className="inline-flex items-center mt-3 text-sm text-blue-600 group-hover:underline">
                                        Zobacz na mapie <Navigation className="w-3.5 h-3.5 ml-1" />
                                    </span>
                                </div>
                              </a>
                            );
                          })}
                        </div>
                      </>
                    )}
                  </AccordionContent>
                </AccordionItem>
              ))}
            </Accordion>
          ) : ( <p className="text-slate-500 text-center py-4">Brak szczegółowego planu.</p> )}
        </section>

        <section className="bg-white p-6 rounded-xl shadow-lg">
            <div className="flex items-center mb-6">
              <MapIconLucide className="w-7 h-7 mr-3 text-green-600" />
              <h2 className="text-2xl md:text-3xl font-semibold text-slate-800">Mapa Podróży</h2>
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
                  {googleMapsApiKey ? 'Brak lokalizacji z prawidłowymi współrzędnymi do wyświetlenia.' : 'Klucz Google Maps API nie jest skonfigurowany, mapa nie może być wyświetlona.'}
                </p>
              </div>
            )}
            
            {validMapLocations.length > 0 && (
              <div className="mt-6">
                <h3 className="text-lg font-semibold text-slate-700 mb-3">Lista kluczowych lokalizacji:</h3>
                <ul className="space-y-1 text-sm max-h-60 overflow-y-auto pr-2">
                  {validMapLocations.map((loc, idx) => (
                    <li 
                      key={idx} 
                      className={`flex items-center text-slate-700 p-2.5 hover:bg-sky-50 rounded-md cursor-pointer ${selectedMapLocation === loc ? 'bg-sky-100' : ''}`}
                      onClick={() => setSelectedMapLocation(loc)}
                    >
                      <MapPinIcon className={`w-5 h-5 mr-2.5 shrink-0 ${selectedMapLocation === loc ? 'text-blue-600 scale-110' : 'text-red-500'}`} />
                      <span className={`font-medium ${selectedMapLocation === loc ? 'text-blue-600' : ''}`}>{loc.name}</span>
                      {loc.day && <span className="text-xs text-slate-400 ml-2">(Dzień {loc.day})</span>}
                      {loc.type && <span className="ml-auto text-xs bg-green-100 text-green-700 px-2 py-0.5 rounded-full">{loc.type}</span>}
                    </li>
                  ))}
                </ul>
              </div>
            )}
        </section>

        {generatedPlan.general_notes && generatedPlan.general_notes.length > 0 && (
          <section className="bg-white p-6 rounded-xl shadow-lg">
             <div className="flex items-center mb-4"> <ClipboardList className="w-7 h-7 mr-3 text-purple-600" />
                <h2 className="text-2xl md:text-3xl font-semibold text-slate-800">Notatki Ogólne</h2>
            </div>
            <ul className="list-disc ml-5 space-y-1 text-slate-700">
              {generatedPlan.general_notes.map((note, idx) => ( <li key={idx}>{note}</li> ))}
            </ul>
          </section>
        )}
<button
  onClick={() => {
    if (!tripId) return;
    setIsGenerationInitiated(true);
    fetchPlan();
  }}
  disabled={loading} 
  className="fixed bottom-6 right-6 bg-blue-600 hover:bg-blue-700 text-white font-medium px-6 py-3 rounded-full shadow-lg z-50 disabled:opacity-50 disabled:cursor-not-allowed"
>
  {loading ? (
    <span className="flex items-center"><Loader2 className="animate-spin w-5 h-5 mr-2" /> Generuję...</span>
  ) : (
    "Wygeneruj ponownie"
  )}
</button>


{/* --- SAVE STATUS --- */}
{saveMessage && (
  <div className="fixed bottom-24 right-6 bg-white border border-slate-200 px-4 py-3 rounded-lg shadow-lg text-slate-700 z-50">
    {saveMessage}
  </div>
)}

      </div>
      <footer className="text-center mt-12 py-6 border-t border-slate-200">
        <p className="text-sm text-slate-500">Plan podróży wygenerowany. Udanej przygody!</p>
      </footer>
    </div>
  );
};
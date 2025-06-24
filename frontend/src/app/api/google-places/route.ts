// app/api/google-places/route.ts
import { NextRequest, NextResponse } from 'next/server';

const GOOGLE_PLACES_API_KEY = process.env.NEXT_PUBLIC_GOOGLE_PLACES_API_KEY;

export async function POST(req: NextRequest) {
  if (!GOOGLE_PLACES_API_KEY) {
    console.error('Google Places API key is not configured on the server.');
    return NextResponse.json({ error: 'Błąd konfiguracji serwera: Klucz API Google Places nie jest ustawiony.' }, { status: 500 });
  }

  try {
    const { operation, query, placeId, fields } = await req.json();
    let apiUrl = '';
    let upstreamErrorMessage = 'Nieprawidłowa operacja lub brakujące parametry dla proxy Google Places.';

    if (operation === 'findplacefromtext' && query) {
      apiUrl = `https://maps.googleapis.com/maps/api/place/findplacefromtext/json?input=${encodeURIComponent(query)}&inputtype=textquery&fields=${fields || 'place_id'}&key=${GOOGLE_PLACES_API_KEY}&language=pl`; // Dodano język polski
      upstreamErrorMessage = `Błąd podczas wyszukiwania miejsca dla zapytania: ${query}`;
    } else if (operation === 'details' && placeId) {
      apiUrl = `https://maps.googleapis.com/maps/api/place/details/json?place_id=${placeId}&fields=${fields || 'photos,url,name,formatted_address,rating'}&key=${GOOGLE_PLACES_API_KEY}&language=pl`; // Dodano język polski
      upstreamErrorMessage = `Błąd podczas pobierania szczegółów dla miejsca: ${placeId}`;
    } else {
      return NextResponse.json({ error: upstreamErrorMessage }, { status: 400 });
    }

    const googleResponse = await fetch(apiUrl);
    const data = await googleResponse.json();

    if (!googleResponse.ok) {
      console.error(`Błąd odpowiedzi z Google API (${operation}, status: ${googleResponse.status}):`, data);
      return NextResponse.json({ error: data.error_message || upstreamErrorMessage, details: data }, { status: googleResponse.status });
    }

    return NextResponse.json(data);

  } catch (error) {
    console.error('Krytyczny błąd w proxy do Google Places API:', error);
    const message = error instanceof Error ? error.message : 'Wewnętrzny błąd serwera w proxy.';
    return NextResponse.json({ error: 'Nie udało się przetworzyć zapytania do Google Places API przez proxy.', details: message }, { status: 500 });
  }
}
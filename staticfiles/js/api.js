


function login() {
    const client_id = process.env.client_id;
    const client_secret = process.env.client_secret;
    const redirect_uri = process.env.redirect_uri;

    const authorizationParams = {
      response_type: 'code',
      client_id: client_id,
      scope: 'user-top-read',
      redirect_uri: redirect_uri
    };
    console.log(redirect_uri)
    const authorizationUrl = 'https://accounts.spotify.com/authorize?' + new URLSearchParams(authorizationParams).toString();
    // Redirect the browser to the authorization URL

   
    window.location.href = authorizationUrl;
}
  

async function auth() {

    const client_id = process.env.client_id;
    const client_secret = process.env.client_secret;
    const redirect_uri = process.env.redirect_uri;
    const urlParams = new URLSearchParams(window.location.search);
    const code = urlParams.get('code');

    const authOptions = {
      url: 'https://accounts.spotify.com/api/token',
      method: 'POST',
      body: new URLSearchParams({
        code: code,
        redirect_uri: redirect_uri,
        grant_type: 'authorization_code'
      }),
      headers: {
        'Authorization': 'Basic ' + btoa(client_id + ':' + client_secret)
      }
    };
    
    try {
      const response = await fetch(authOptions.url, {
        method: authOptions.method,
        body: authOptions.body,
        headers: authOptions.headers
      });
  
      if (response.status === 200) {
        const responseData = await response.json();
        console.log("response:",responseData)
        const access_token = responseData.access_token;
        const token_type = responseData.token_type;
        const scope = responseData.scope;
        const expires_in = responseData.expires_in;
        const refresh_token = responseData.refresh_token;
  
        const now = new Date();
        const expires = new Date(now.getTime() + expires_in * 1000);


        localStorage.setItem('access_token', access_token);
        localStorage.setItem('expires_in', expires_in);
        localStorage.setItem('refresh_token', refresh_token);
        localStorage.setItem('expires', expires);

  
        if (expires <= now) {
            refreshSpotifyToken()
        } 
      } else {    
        
      }
    } catch (error) {
      // Handle network or other errors
      console.error(error);
    }
}
  
async function refreshSpotifyToken() {
    const client_id = process.env.client_id;
    const client_secret = process.env.client_secret;
    const redirect_uri = process.env.redirect_uri;
    
    const tokenUrl =  "https://accounts.spotify.com/api/token"

    const refreshToken = localStorage.getItem('refresh_token');


    const headers = {
      'Authorization': 'Basic ' + btoa(client_id + ':' + client_secret)
    };
  
    const data = new URLSearchParams({
      'grant_type': 'refresh_token',
      'refresh_token': refreshToken
    });
  
    try {
      const response = await fetch(tokenUrl, {
        method: 'POST',
        headers: headers,
        body: data
      });
  
      if (response.status === 200) {
        const responseData = await response.json();
        const access_token = responseData.access_token;
        const token_type = responseData.token_type;
        const scope = responseData.scope;
        const expires_in = responseData.expires_in;
        const newRefreshToken = responseData.refresh_token || refreshToken; // Refresh token may or may not be included
  
        const now = new Date();
        const expires = new Date(now.getTime() + expires_in * 1000);
  
        // Update instance variables with new token data if needed
  
        localStorage.setItem('access_token', access_token);
        localStorage.setItem('expires_in', expires_in);
        localStorage.setItem('refresh_token', newRefreshToken);
        localStorage.setItem('expires', expires);
  
      } else {
        // Handle the error condition here
        // You can return an error response or handle it as needed
        return null;
      }
    } catch (error) {
      // Handle network or other errors
      console.error(error);
      return null;
    }
}
  

const getTopTracks = async (time_range,limit) => {

    access_token = localStorage.getItem('access_token');
    console.log("access token", access_token) 

    const url = new URL('https://api.spotify.com/v1/me/top/tracks');

    // Create an instance of URLSearchParams to handle query parameters
    const params = new URLSearchParams();
    
    // Add query parameters to the params object
    params.append('limit', encodeURIComponent(limit));
    params.append('time_range', encodeURIComponent(time_range));
    
    
    // Append the query parameters to the URL
    url.search = params.toString();
    
    const headers = {
    'Authorization': `Bearer ${access_token}`

    };
  
    console.log("header", headers)
    console.log("url",url)

    const response = await fetch(url,{
        method:'GET',
        headers: headers,
        
    });

    console.log(response.status);


    const data = await response.json();
    console.log("data",data)
    return data
} 

async function populateTopTracks(time_range,limit) {
    console.log(time_range)
    localStorage.setItem('time_range', time_range);
    localStorage.setItem('limit', limit);

    try {
        const topTracks = await getTopTracks(time_range,limit); // Call your function to get top tracks

        const olElement = document.querySelector('.track-grid'); // Get the <ol> element
        
        olElement.innerHTML = '';


        const h1Element = document.querySelector('h1');


        // Map button IDs to time_range values
        const timeRangeMap = {
            short_term: "1 Month",
            medium_term: "6 Months",
            long_term: "All Time",
        };

        // Get the corresponding time_range from the map
        const timeRange = timeRangeMap[time_range];    

        h1Element.textContent = 'Your Top ' + limit + ' Tracks - ' + timeRange;


        // Loop through the top_tracks data and create list items for each item
        topTracks.items.forEach((item) => {
            const liElement = document.createElement('li'); // Create a new <li> element

            // Create an <img> element for the album cover
            const imgElement = document.createElement('img');
            imgElement.src = item.album.images[0].url;
            imgElement.alt = 'Album Cover';

            // Create a <figcaption> element for the track information
            const figcaptionElement = document.createElement('figcaption');
            figcaptionElement.innerHTML = `<strong>${item.name}</strong> by ${item.artists[0].name}`;

            // Append the <img> and <figcaption> elements to the <li> element
            liElement.appendChild(imgElement);
            liElement.appendChild(figcaptionElement);

            // Append the <li> element to the <ol> element
            olElement.appendChild(liElement);
        });
    } catch (error) {
        console.error('Error fetching and populating top tracks:', error);
    }
}

const getTopArtists = async (time_range,limit) => {

    access_token = localStorage.getItem('access_token');
    console.log("access token", access_token) 

    const url = new URL('https://api.spotify.com/v1/me/top/artists');

    // Create an instance of URLSearchParams to handle query parameters
    const params = new URLSearchParams();
    
    // Add query parameters to the params object
    params.append('limit', encodeURIComponent(limit));
    params.append('time_range', encodeURIComponent(time_range));
    
    
    // Append the query parameters to the URL
    url.search = params.toString();
    
    const headers = {
    'Authorization': `Bearer ${access_token}`

    };
  
    console.log("header", headers)
    console.log("url",url)

    const response = await fetch(url,{
        method:'GET',
        headers: headers,
        
    });

    console.log(response.status);


    const data = await response.json();
    console.log("data",data)
    return data
} 

async function populateTopArtists(time_range,limit) {
    console.log(time_range)
    localStorage.setItem('time_range', time_range);
    localStorage.setItem('limit', limit);
    
    try {
        const topArtists = await getTopArtists(time_range,limit); // Call your function to get top Artists

        const olElement = document.querySelector('.track-grid'); // Get the <ol> element
        
        olElement.innerHTML = '';
        const h1Element = document.querySelector('h1');


        // Map button IDs to time_range values
        const timeRangeMap = {
            short_term: "1 Month",
            medium_term: "6 Months",
            long_term: "All Time",
        };

        // Get the corresponding time_range from the map
        const timeRange = timeRangeMap[time_range];    

        h1Element.textContent = 'Your Top ' + limit + ' Artists - ' + timeRange;

        // Loop through the top_Artists data and create list items for each item
        topArtists.items.forEach((item) => {
            const liElement = document.createElement('li'); // Create a new <li> element

            // Create an <img> element for the artist picture
            const imgElement = document.createElement('img');
            imgElement.src = item.images[0].url;
            imgElement.alt = 'Artist Image';

            // Create a <figcaption> element for the artist name
            const figcaptionElement = document.createElement('figcaption');
            figcaptionElement.innerHTML = `<strong>${item.name}</strong>`;

            // Append the <img> and <figcaption> elements to the <li> element
            liElement.appendChild(imgElement);
            liElement.appendChild(figcaptionElement);

            // Append the <li> element to the <ol> element
            olElement.appendChild(liElement);
        });
    } catch (error) {
        console.error('Error fetching and populating top Artists:', error);
    }
}


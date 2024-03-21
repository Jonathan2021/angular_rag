const { REACT_APP_API_BASE_URL } = process.env;

async function request<T>(uri: string, options?: RequestInit): Promise<T> {
    const response = await fetch(`${REACT_APP_API_BASE_URL}${uri}`, options);

    if (!response.ok) {
      throw new Error(`Request failed with status ${response.status}`);
    }

    return response.json();
}
  
export default {
    get<T>(uri: string, options?: RequestInit): Promise<T> {
      return request<T>(uri, { method: 'GET', ...options });
    },
    post<T>(uri: string, body: any, options?: RequestInit): Promise<T> {
      return request<T>(uri, { method: 'POST', body: JSON.stringify(body), ...options });
    },
};
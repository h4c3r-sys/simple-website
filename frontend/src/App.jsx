import React, { useState } from 'react';
import axios from 'axios';

// Assuming backend is on localhost:8000 for now.
// In Docker, this might need adjustment or a proxy, but localhost usually works for browser->backend.
const API_URL = 'http://localhost:8000';

function App() {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(false);
  const [sourcing, setSourcing] = useState({}); // Map of product ID to loading state
  const [sourcedLinks, setSourcedLinks] = useState({}); // Map of product ID to links

  const handleScan = async () => {
    setLoading(true);
    try {
      const response = await axios.post(`${API_URL}/api/scan`);
      // Sort by Hype Score descending
      const sortedProducts = response.data.sort((a, b) => b.hype_score - a.hype_score);
      setProducts(sortedProducts);
    } catch (error) {
      console.error("Error scanning trends:", error);
      alert("Failed to scan trends. Check backend console.");
    }
    setLoading(false);
  };

  const handleApprove = async (product) => {
    if (!product.product_name) {
      alert("No product name identified to source.");
      return;
    }

    setSourcing(prev => ({ ...prev, [product.id]: true }));
    try {
      const response = await axios.post(`${API_URL}/api/source`, {
        product_name: product.product_name
      });
      setSourcedLinks(prev => ({ ...prev, [product.id]: response.data.links }));
    } catch (error) {
      console.error("Error sourcing product:", error);
      alert("Failed to find links.");
    }
    setSourcing(prev => ({ ...prev, [product.id]: false }));
  };

  const handleReject = (id) => {
    setProducts(prev => prev.filter(p => p.id !== id));
  };

  return (
    <div className="min-h-screen bg-gray-900 text-gray-100 p-8 font-sans">
      <header className="mb-10 text-center">
        <h1 className="text-4xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-purple-500 mb-2">
          Viral Product Hunter
        </h1>
        <p className="text-gray-400">Find, Analyze, and Source the next big thing.</p>
      </header>

      <div className="max-w-4xl mx-auto mb-8 text-center">
        <button
          onClick={handleScan}
          disabled={loading}
          className={`px-8 py-4 rounded-full text-lg font-semibold shadow-lg transition-all transform hover:scale-105 ${
            loading
              ? "bg-gray-700 cursor-not-allowed"
              : "bg-blue-600 hover:bg-blue-500 text-white shadow-blue-500/50"
          }`}
        >
          {loading ? "Scanning Social Media..." : "🔍 Scan for Viral Trends"}
        </button>
      </div>

      <div className="max-w-5xl mx-auto space-y-6">
        {products.map((product) => (
          <div key={product.id} className="bg-gray-800 rounded-xl p-6 shadow-lg border border-gray-700 flex flex-col md:flex-row gap-6">

            {/* Left: Product Info */}
            <div className="flex-1">
              <div className="flex items-center justify-between mb-2">
                <h2 className="text-xl font-bold text-white">{product.product_name || "Unknown Product"}</h2>
                <span className={`px-3 py-1 rounded-full text-sm font-bold ${
                  product.hype_score >= 80 ? "bg-green-500/20 text-green-400" :
                  product.hype_score >= 50 ? "bg-yellow-500/20 text-yellow-400" :
                  "bg-red-500/20 text-red-400"
                }`}>
                  Hype Score: {product.hype_score}
                </span>
              </div>
              <p className="text-gray-300 text-sm mb-3">{product.snippet}</p>
              <p className="text-purple-400 text-sm italic">" {product.reason} "</p>
              <div className="mt-2">
                <a href={product.original_link} target="_blank" rel="noopener noreferrer" className="text-blue-400 hover:underline text-xs">
                  View Original Post
                </a>
              </div>
            </div>

            {/* Right: Actions & Results */}
            <div className="md:w-64 flex flex-col justify-between border-l border-gray-700 md:pl-6 pt-4 md:pt-0">

              {!sourcedLinks[product.id] ? (
                <div className="flex gap-2">
                  <button
                    onClick={() => handleApprove(product)}
                    disabled={sourcing[product.id]}
                    className="flex-1 bg-green-600 hover:bg-green-500 text-white py-2 rounded transition-colors"
                  >
                    {sourcing[product.id] ? "Sourcing..." : "✅ Approve"}
                  </button>
                  <button
                    onClick={() => handleReject(product.id)}
                    className="flex-1 bg-red-600 hover:bg-red-500 text-white py-2 rounded transition-colors"
                  >
                    ❌ Reject
                  </button>
                </div>
              ) : (
                <div className="animate-fade-in">
                  <h3 className="text-sm font-bold text-gray-400 mb-2">AliExpress Links:</h3>
                  <ul className="space-y-2">
                    {sourcedLinks[product.id].map((link, i) => (
                      <li key={i}>
                        <a
                          href={link.link}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="block bg-gray-700 hover:bg-gray-600 p-2 rounded text-xs text-blue-300 truncate"
                          title={link.title}
                        >
                          🛒 {link.title.substring(0, 25)}...
                        </a>
                      </li>
                    ))}
                    {sourcedLinks[product.id].length === 0 && <li className="text-xs text-gray-500">No links found.</li>}
                  </ul>
                </div>
              )}

            </div>
          </div>
        ))}

        {products.length === 0 && !loading && (
          <div className="text-center text-gray-500 mt-10">
            <p>No trends found yet. Hit the scan button!</p>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;

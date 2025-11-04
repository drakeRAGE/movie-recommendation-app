import { useState } from "react";
import axios from "axios";

interface Movie {
  title: string;
  year?: string;
  reason?: string;
}

export default function App() {
  const [input, setInput] = useState("");
  const [movies, setMovies] = useState<Movie[]>([]);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim()) return;

    setLoading(true);
    setMovies([]);

    try {
      const res = await axios.post("http://127.0.0.1:8000/recommend", {
        user_input: input,
      });
      setMovies(res.data.recommended_movies);
    } catch (err) {
      console.error(err);
      alert("Error fetching recommendations.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#0d0d0f] text-white flex flex-col items-center justify-center px-4">
      <div className="w-full max-w-2xl p-8 bg-[#16161a] rounded-2xl shadow-lg border border-[#27272a]">
        <h1 className="text-3xl font-semibold text-center mb-6 text-white">
          🎬 Movie Recommendation App
        </h1>

        <form
          onSubmit={handleSubmit}
          className="flex flex-col md:flex-row gap-4 items-center"
        >
          <input
            type="text"
            placeholder='e.g. "action movies with a strong female lead"'
            value={input}
            onChange={(e) => setInput(e.target.value)}
            className="flex-1 bg-[#1c1c21] text-gray-100 placeholder-gray-400 rounded-xl px-4 py-3 outline-none focus:ring-2 focus:ring-purple-500 border border-[#2a2a2f] transition-all"
          />
          <button
            type="submit"
            disabled={loading}
            className={`px-6 py-3 rounded-xl font-medium transition-all ${loading
                ? "bg-purple-800 text-gray-300 cursor-not-allowed"
                : "bg-gradient-to-r from-purple-600 to-indigo-600 hover:scale-105 active:scale-95"
              }`}
          >
            {loading ? "Generating..." : "Get Recommendations"}
          </button>
        </form>

        {movies.length > 0 && (
          <div className="mt-8">
            <h2 className="text-2xl font-semibold mb-4 text-gray-100">
              Recommended Movies
            </h2>
            <ul className="grid grid-cols-1 sm:grid-cols-2 gap-6 mt-8">
              {movies.map((movie, i) => (
                <li
                  key={i}
                  className="relative group p-5 rounded-2xl bg-[#151518]/80 backdrop-blur-md border border-[#26262a] hover:border-purple-500/70 transition-all duration-300 hover:shadow-[0_0_20px_rgba(168,85,247,0.2)] hover:-translate-y-1"
                >
                  {/* subtle gradient overlay */}
                  <div className="absolute inset-0 bg-gradient-to-br from-purple-600/10 via-transparent to-indigo-600/10 rounded-2xl opacity-0 group-hover:opacity-100 transition-opacity duration-300" />

                  <div className="relative z-10">
                    <h3 className="text-xl font-semibold text-white flex items-center gap-2">
                      🎞 <span className="text-purple-400">{movie.title}</span>
                      {movie.year && (
                        <span className="text-sm text-gray-400 ml-1">({movie.year})</span>
                      )}
                    </h3>

                    {movie.reason && (
                      <p className="text-gray-300 mt-3 leading-relaxed text-sm">
                        {movie.reason}
                      </p>
                    )}

                    <button
                      className="mt-4 px-4 py-2 rounded-lg bg-gradient-to-r from-purple-600 to-indigo-600 text-sm font-medium text-white opacity-0 group-hover:opacity-100 transition-all duration-300 hover:scale-105 active:scale-95"
                    >
                      More Info
                    </button>
                  </div>
                </li>
              ))}
            </ul>

          </div>
        )}

        {!loading && movies.length === 0 && (
          <p className="mt-10 text-gray-400 text-center">
            Type your movie preference above and get AI-powered suggestions 🎥
          </p>
        )}
      </div>

      <footer className="mt-10 text-gray-500 text-sm">
        Made by <span className="text-purple-400">Deepak Joshi</span>
      </footer>
    </div>
  );
}

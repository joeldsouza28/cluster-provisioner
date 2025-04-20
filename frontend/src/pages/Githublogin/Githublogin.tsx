import { getAuthUrl } from "../../services";


export default function GithubLogin() {

  const handleLogin = () => {
    window.location.href = getAuthUrl(); // or your backend URL
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-100">
      <button
        onClick={handleLogin}
        className="bg-gray-900 text-white px-4 py-2 rounded-md flex items-center gap-2 hover:bg-gray-800"
      >
        <svg
          className="w-5 h-5"
          fill="currentColor"
          viewBox="0 0 24 24"
        >
          <path d="M12 0C5.371 0 0 5.373 0 12c0 5.302 3.438 9.8 8.205 11.387.6.111.82-.26.82-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.385-1.333-1.754-1.333-1.754-1.089-.745.083-.729.083-.729 1.205.085 1.838 1.237 1.838 1.237 1.07 1.834 2.809 1.304 3.495.996.108-.776.419-1.305.762-1.604-2.665-.304-5.467-1.334-5.467-5.931 0-1.31.468-2.381 1.235-3.221-.123-.303-.535-1.523.117-3.176 0 0 1.008-.322 3.301 1.23A11.52 11.52 0 0112 6.844c1.02.005 2.047.138 3.007.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.241 2.873.118 3.176.77.84 1.233 1.911 1.233 3.221 0 4.61-2.807 5.625-5.48 5.921.43.37.814 1.102.814 2.222v3.293c0 .32.218.694.825.576C20.565 21.796 24 17.299 24 12c0-6.627-5.373-12-12-12z" />
        </svg>
        Sign in with GitHub
      </button>
    </div>
  );
};


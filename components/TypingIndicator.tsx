"use client"

export function TypingIndicator() {
  return (
    <div className="flex items-center justify-start gap-2 p-2 rounded-full bg-green-100/30 max-w-[60px]">
      <span className="dot animate-dot1"></span>
      <span className="dot animate-dot2"></span>
      <span className="dot animate-dot3"></span>

      <style jsx>{`
        .dot {
          width: 8px;
          height: 8px;
          background-color: #121312ff; /* Vert WhatsApp */
          border-radius: 50%;
          display: inline-block;
        }

        .animate-dot1 {
          animation: bounce 1.4s infinite ease-in-out;
        }

        .animate-dot2 {
          animation: bounce 1.4s infinite ease-in-out 0.2s;
        }

        .animate-dot3 {
          animation: bounce 1.4s infinite ease-in-out 0.4s;
        }

        @keyframes bounce {
          0%, 80%, 100% {
            transform: scale(0);
          }
          40% {
            transform: scale(1);
          }
        }
      `}</style>
    </div>
  )
}

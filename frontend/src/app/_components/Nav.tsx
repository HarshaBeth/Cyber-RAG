"use client";
import { useState } from "react";
import { MessageSquare, BookOpen } from "lucide-react";
import Link from "next/link";

const NavItems = [
  { icon: MessageSquare, label: "Chat", link: "/chat" },
  { icon: BookOpen, label: "Knowledge", link: "/knowledge" },
];

function Nav() {
  const [isExpanded, setIsExpanded] = useState(false);

  return (
    <div
      className={`sticky top-0 h-screen shrink-0 overflow-y-auto bg-[#121826] py-7 transition-all ${isExpanded ? "w-52" : "w-20"} relative flex flex-col items-center self-start`}
    >
      <div
        className={`absolute ${isExpanded ? "right-2 top-7" : ""} bg-[#1a2337] rounded-md hover:cursor-pointer`}
      >
        <button
          className="text-white rounded-md px-2 py-0.5 border-zinc-500/45 border-2"
          onClick={() => setIsExpanded(!isExpanded)}
        >
          {isExpanded ? "X" : "O"}
        </button>
      </div>

      <div className="font-serif pt-20">
        {NavItems.map((item) => {
          const Icon = item.icon;

          return (
            <Link
              href={item.link}
              key={item.label}
              className="flex items-center gap-4 text-white hover:bg-[#1a2337] px-3 py-2 rounded-md cursor-pointer transition-colors"
            >
              <Icon size={20} />
              {isExpanded && <span className=" font-medium">{item.label}</span>}
            </Link>
          );
        })}
      </div>
    </div>
  );
}

export default Nav;

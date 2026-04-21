import Image from "next/image";
import Nav from "./_components/Nav";

export default function Home() {
  return (
    <div className="flex h-screen w-screen bg-zinc-50 font-sans text-black">
      <div className="flex flex-1 items-center justify-center">
        <div>Hello World</div>
      </div>
    </div>
  );
}

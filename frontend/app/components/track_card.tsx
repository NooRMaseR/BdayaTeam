import { Card, CardContent } from "@mui/material";
import Link from "next/link";

export default function TrackCard({ title, desc, url = `#${title}` }: { url?: string, title: string, desc: string }) {
  return (
    <Link href={url} className="h-fit">
      <Card id={title} className="hover:shadow-xl transition-shadow duration-300 border-t-4 border-transparent hover:border-blue-500 hover:scale-110 cursor-pointer" sx={{ transition: "scale ease-out 300ms, border-color ease-out 300ms;", width: "20rem", height: "10rem" }}>
        <CardContent className="flex flex-col items-center text-center p-8">
          <h3 className="text-xl font-bold text-gray-800 mb-2">{title}</h3>
          <p className="text-gray-600 text-sm leading-relaxed line-clamp-3 overflow-hidden">
            {desc}
          </p>
        </CardContent>
      </Card>
    </Link>
  )
}
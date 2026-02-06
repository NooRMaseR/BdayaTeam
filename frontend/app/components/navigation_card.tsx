import CardContent from "@mui/material/CardContent";
import Typography from "@mui/material/Typography";
import CardMedia from "@mui/material/CardMedia";
import Card from "@mui/material/Card";

import { Link } from "@/i18n/navigation";
import { ReactNode } from "react";
import Image from "next/image";

type NavigationCardProps = {
  url?: string;
  imageUrl?: string | null;
  title: string;
  desc: string | ReactNode;
};

export default function NavigationCard({ title, desc, imageUrl, url = `#${title}` }: NavigationCardProps) {
  if (desc instanceof String) {

  }
  return (
    <Link href={url} className="h-auto">
      <Card id={title} className="hover:shadow-xl transition-shadow duration-250 border-t-4 border-transparent hover:border-blue-500 hover:scale-105 cursor-pointer" sx={{ transition: "scale ease-out 250ms, border-color ease-out 250ms;", width: "20rem", height: "19rem" }}>
        {
          imageUrl
            ? <CardMedia sx={{ position: 'relative', width: 'auto', height: "11rem" }}>
              <Image src={imageUrl} alt={`track ${title} Image`} fill unoptimized />
            </CardMedia>
            : null
        }
        <CardContent className={`flex flex-col items-center text-center p-8 justify-center ${!imageUrl ? 'h-full' : ''}`}>
          <Typography component={'h5'} variant="h5" sx={{ fontWeight: "bold" }}>{title}</Typography>
          {
            desc instanceof String ? (
              <Typography component={'p'} variant="subtitle1" color="textSecondary" className="leading-relaxed line-clamp-2">
                {desc}
              </Typography>
            ) : desc
          }
        </CardContent>
      </Card>
    </Link>
  )
}
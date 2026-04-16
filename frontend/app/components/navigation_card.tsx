import CardContent from "@mui/material/CardContent";
import Typography from "@mui/material/Typography";
import CardMedia from "@mui/material/CardMedia";
import Badge from "@mui/material/Badge";
import Card from "@mui/material/Card";

import { Link } from "@/i18n/navigation";
import { ReactNode } from "react";
import Image from "next/image";

type NavigationCardProps = {
  url?: string;
  imageUrl?: string | null;
  title: string;
  desc: string | ReactNode;
  badgeContent?: number;
};

const RenderLinkOrDiv = ({ url, children }: { url?: string, children: ReactNode }) => {
  if (!url) {
    return <div className="h-full block">{children}</div>;
  }

  if (url.startsWith('http')) {
    return (
      <a href={url} target="_blank" rel="noopener noreferrer" className="h-full block">
        {children}
      </a>
    );
  }
  return <Link href={url} className="h-full block">{children}</Link>;
};

export default function NavigationCard({ title, desc, imageUrl, url, badgeContent = 0 }: NavigationCardProps) {
  return (
    <RenderLinkOrDiv url={url}>
      <Card
        id={title}
        className="hover:shadow-xl dark:hover:shadow-2xl dark:hover:shadow-black/50 border-t-4 border-transparent hover:border-blue-500 dark:hover:border-blue-400 hover:-translate-y-2 cursor-pointer flex flex-col"
        sx={{ transition: "translate ease-out 250ms, border-color ease-out 250ms, box-shadow ease-out 250ms", width: "20rem", height: "19rem" }}
      >
        <Badge className="flex flex-col" badgeContent={badgeContent} color="error" anchorOrigin={{ vertical: "top", horizontal: "left" }} sx={{ mt: "1rem", ml: "1rem"}}>

          {imageUrl && (
            <CardMedia sx={{ position: 'relative', width: '100%', height: "11rem" }}>
              <Image
                src={imageUrl}
                alt={`${title} Track`}
                fill
                style={{ objectFit: 'cover' }}
                unoptimized
                className="dark:opacity-90 dark:brightness-90 transition-all duration-300" 
              />
            </CardMedia>
          )}

          <CardContent className={`flex flex-col items-center text-center p-6 grow justify-center ${!imageUrl ? 'h-full' : ''}`}>
            <Typography component="h5" variant="h5" sx={{ fontWeight: "bold", mb: 1 }}>
              {title}
            </Typography>

            {typeof desc === 'string' ? (
              <Typography component="p" variant="subtitle2" color="text.secondary" className="leading-relaxed line-clamp-2">
                {desc}
              </Typography>
            ) : (
              desc
            )}
          </CardContent>
        </Badge>
      </Card>
    </RenderLinkOrDiv>
  );
}
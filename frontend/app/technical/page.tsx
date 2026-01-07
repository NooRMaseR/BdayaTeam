import { Card, CardActionArea, CardContent } from "@mui/material";
import { Metadata } from "next";
import Link from "next/link";

export const metadata: Metadata = {
  title: "Technical Team Bdaya",
  description: "Technical Team Bdaya, Come and manage your members tasks and create some tasks for them",
  keywords: "Technical,technical,Tasks,Members,Profile",
  openGraph: {
    title: `Technical Team Bdaya:`,
    description: 'Technical Team Bdaya, Come and manage your members tasks and create some tasks for them',
    images: [`/bdaya_black.png`], 
  },
}

export default function TechnicalPage() {
  const cards = [
    { title: "See Tasks", link: "/tasks" },
    { title: "See Members", link: "/members" },
    { title: "See Member Profile", link: "/profile" },
  ];
  return (
    <main className="w-full flex gap-6 justify-center flex-wrap">
      {cards.map((item, index) => (
        <Card
          key={index}
          sx={{
            width: "20rem",
            height: "20rem",
            borderRadius: "1rem",
            boxShadow: "0 4px 10px rgba(0, 0, 0, 0.1)",
            transition: "transform 0.2s, box-shadow 0.2s",
            "&:hover": {
              transform: "scale(1.05)",
              boxShadow: "0 6px 15px rgba(0, 0, 0, 0.2)",
            },
          }}
        >
          <Link href={item.link}>
            <CardActionArea sx={{ width: "100%", height: "100%" }}>
              <CardContent
                sx={{
                  textAlign: "center",
                  display: "flex",
                  flexDirection: "column",
                  justifyContent: "center",
                  alignItems: "center",
                  height: "100%",
                }}
              >
                <h1 className="text-xl font-semibold text-gray-700">
                  {item.title}
                </h1>
              </CardContent>
            </CardActionArea>
          </Link>
        </Card>
      ))}
    </main>
  );
}

"use client";

import { useState } from "react";
import Box from "@mui/material/Box";
import Button from "@mui/material/Button";
import Typography from "@mui/material/Typography";
import { keyframes, useTheme } from "@mui/material";
import WifiOffIcon from "@mui/icons-material/WifiOff";
import RefreshIcon from "@mui/icons-material/Refresh";

const ping = keyframes`
  0% { transform: scale(1); opacity: 0.5; }
  100% { transform: scale(2.5); opacity: 0; }
`;

const pulse = keyframes`
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
`;

const bounce = keyframes`
  0%, 100% { transform: translateY(-10%); }
  50% { transform: translateY(10%); }
`;

export default function OfflinePage() {
  const theme = useTheme();
  const [isHovered, setIsHovered] = useState(false);

  return (
    <Box
      sx={{
        minHeight: "calc(100vh - 105px)",
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        p: 3,
        textAlign: "center",
        bgcolor: "transparent",
      }}
    >
      {/* The Animated Radar/Pulse Effect */}
      <Box sx={{ position: "relative", mb: 6, display: "flex", alignItems: "center", justifyContent: "center" }}>
        {/* Outer expanding ring */}
        <Box
          className="dark:bg-(--dark-color)"
          sx={{
            position: "absolute",
            width: 120,
            height: 120,
            borderRadius: "50%",
            opacity: 0.2,
            animation: `${ping} 3s cubic-bezier(0, 0, 0.2, 1) infinite`,
          }}
        />
        {/* Inner pulsing glow */}
        <Box
          sx={{
            position: "absolute",
            width: 90,
            height: 90,
            borderRadius: "50%",
            bgcolor: theme.palette.error.main,
            opacity: 0.3,
            animation: `${pulse} 2s cubic-bezier(0.4, 0, 0.6, 1) infinite`,
            filter: "blur(8px)",
          }}
        />

        {/* Icon Container */}
        <Box
          sx={{
            position: "relative",
            bgcolor: theme.palette.background.paper,
            p: 3,
            borderRadius: "50%",
            boxShadow: theme.shadows[6],
            border: `1px solid ${theme.palette.divider}`,
            zIndex: 1,
          }}
        >
          <WifiOffIcon
            color="error"
            sx={{
              fontSize: 64,
              animation: `${bounce} 2s ease-in-out infinite`,
            }}
          />
        </Box>
      </Box>

      <Typography variant="h3" sx={{ fontWeight: 800, mb: 2, letterSpacing: "-0.02em" }}>
        Connection Lost
      </Typography>
      
      <Typography variant="body1" color="text.secondary" sx={{ maxWidth: 450, mb: 5, lineHeight: 1.7 }}>
        It looks like you&lsquo;re offline. Please check your internet connection and we&lsquo;ll get you right back into Team Bdaya.
      </Typography>

      <Button
        variant="contained"
        size="large"
        startIcon={
          <RefreshIcon
            sx={{
              transition: "transform 0.7s ease",
              transform: isHovered ? "rotate(180deg)" : "rotate(0deg)",
            }}
          />
        }
        onClick={() => window.location.reload()}
        onMouseEnter={() => setIsHovered(true)}
        onMouseLeave={() => setIsHovered(false)}
        sx={{
          borderRadius: 8,
          px: 4,
          py: 1.5,
          fontWeight: 700,
          textTransform: "none",
          fontSize: "1.1rem",
          boxShadow: theme.shadows[4],
          "&:hover": {
            boxShadow: theme.shadows[10],
            transform: "translateY(-2px)",
          },
          transition: "all 0.3s ease",
        }}
      >
        Try Again
      </Button>
    </Box>
  );
}
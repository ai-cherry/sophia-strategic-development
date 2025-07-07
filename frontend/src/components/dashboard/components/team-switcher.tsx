import React from "react";
import { Button } from "@/components/ui/button";

export default function TeamSwitcher() {
  return (
    <Button variant="ghost" className="h-9 w-9 p-0">
      <span className="sr-only">Team Switcher</span>
      <span className="h-5 w-5 rounded-sm bg-primary text-primary-foreground flex items-center justify-center text-xs font-bold">
        S
      </span>
    </Button>
  );
}

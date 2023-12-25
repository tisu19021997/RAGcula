'use client';
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { Props } from "@/app/interfaces/iprops.interface";

const queryClient = new QueryClient();

export const ProvidesTheQueryClient = ({ children }: Props) => {
   return (
      <QueryClientProvider client={queryClient}>
         {children}
      </QueryClientProvider>
   );
}
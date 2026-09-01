import { api } from "./api";

export const documentService = {
  upload: (data) =>
    api("/documents/", {
      method: "POST",
      body: data,
    }),
};
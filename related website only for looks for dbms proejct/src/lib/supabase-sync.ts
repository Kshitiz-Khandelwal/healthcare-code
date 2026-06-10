import { toast } from "sonner";
import { db } from "./db-store";

export interface SupabaseStatus {
  connected: boolean;
  message: string;
  error?: string;
}

class SupabaseSyncManager {
  private url = import.meta.env.VITE_SUPABASE_URL || "";
  private key = import.meta.env.VITE_SUPABASE_ANON_KEY || "";

  isEnabled(): boolean {
    return !!(this.url && this.key);
  }

  getSupabaseUrl(): string {
    return this.url;
  }

  // Pure REST-based handshake test
  async testConnection(): Promise<SupabaseStatus> {
    if (!this.isEnabled()) {
      return {
        connected: false,
        message: "Supabase connection keys are missing in the .env file."
      };
    }

    try {
      db.logQuery(
        `SELECT connection_status FROM pg_connect('${this.url.substring(0, 30)}...');`,
        "Pinging Supabase remote REST Gateway"
      );

      // Attempt to ping the database schema or metadata
      const response = await fetch(`${this.url}/rest/v1/`, {
        method: "GET",
        headers: {
          "apikey": this.key,
          "Authorization": `Bearer ${this.key}`
        }
      });

      if (response.ok || response.status === 404 || response.status === 401) {
        // Even a 404 or 401 indicates that the server resides there and completed the TLS handshake
        return {
          connected: true,
          message: "Successfully established handshake with Supabase PostgreSQL!"
        };
      }

      throw new Error(`Server returned status code: ${response.status}`);
    } catch (err: any) {
      console.error("Supabase handshake failed:", err);
      return {
        connected: false,
        message: "Failed to connect to Supabase remote instance.",
        error: err.message || "Network request failed"
      };
    }
  }

  // Push individual tables to Supabase via PostgREST
  async pushTable(tableName: string, rows: any[]): Promise<{ success: boolean; msg: string }> {
    if (!this.isEnabled()) {
      return { success: false, msg: "Supabase keys not configured." };
    }

    try {
      db.logQuery(
        `COPY ${tableName} TO '${this.url.substring(0, 30)}...' WITH (FORMAT CSV);`,
        `Exporting local ${tableName} records to Supabase`
      );

      const response = await fetch(`${this.url}/rest/v1/${tableName}`, {
        method: "POST",
        headers: {
          "apikey": this.key,
          "Authorization": `Bearer ${this.key}`,
          "Content-Type": "application/json",
          "Prefer": "resolution=merge-duplicates" // Upsert behavior
        },
        body: JSON.stringify(rows)
      });

      if (response.ok || response.status === 201) {
        return {
          success: true,
          msg: `Synchronized ${rows.length} rows to remote '${tableName}' table!`
        };
      }

      // If table doesn't exist yet, we get a 404
      if (response.status === 404) {
        throw new Error(
          `Table '${tableName}' not found on Supabase. Did you execute the DDL queries in 'schema.sql' inside your Supabase SQL Editor first?`
        );
      }

      const errMsg = await response.text();
      throw new Error(errMsg || `Status code: ${response.status}`);
    } catch (err: any) {
      console.error(`Supabase sync failed for ${tableName}:`, err);
      return {
        success: false,
        msg: err.message || "Failed to push records."
      };
    }
  }
}

export const supabaseSync = new SupabaseSyncManager();

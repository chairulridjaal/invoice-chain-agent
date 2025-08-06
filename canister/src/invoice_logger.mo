import Debug "mo:base/Debug";
import Time "mo:base/Time";
import Map "mo:base/HashMap";
import Text "mo:base/Text";
import Array "mo:base/Array";
import Iter "mo:base/Iter";
import Nat "mo:base/Nat";
import Int "mo:base/Int";

actor InvoiceLogger {
    
    // Define invoice record type with enhanced fields for chat agent
    public type InvoiceRecord = {
        id: Text;
        vendor_name: Text;
        tax_id: Text;
        amount: Float;
        date: Text;
        status: Text;           // "approved", "rejected", "approved_with_conditions"
        explanation: Text;
        timestamp: Int;
        blockchain_hash: ?Text;
        riskScore: Nat;        // 0-100 risk assessment score
        validationScore: Nat;  // 0-100 overall validation score
        fraudRisk: Text;       // "LOW", "MEDIUM", "HIGH"
        processedAt: Int;      // Processing timestamp
        auditHash: ?Text;      // Hash for audit transparency
    };

    // Define audit log type
    public type AuditLog = {
        invoice_id: Text;
        action: Text;
        timestamp: Int;
        details: Text;
    };

    // Storage for invoices and audit logs
    private stable var invoiceEntries : [(Text, InvoiceRecord)] = [];
    private stable var auditEntries : [(Text, AuditLog)] = [];
    private var invoices = Map.fromIter<Text, InvoiceRecord>(invoiceEntries.vals(), invoiceEntries.size(), Text.equal, Text.hash);
    private var auditLogs = Map.fromIter<Text, AuditLog>(auditEntries.vals(), auditEntries.size(), Text.equal, Text.hash);

    // Counter for audit log IDs
    private stable var auditCounter : Nat = 0;

    // Store invoice record with enhanced validation data
    public func storeInvoice(
        id: Text,
        vendor_name: Text,
        tax_id: Text,
        amount: Float,
        date: Text,
        status: Text,
        explanation: Text,
        blockchain_hash: ?Text,
        riskScore: Nat,
        validationScore: Nat,
        fraudRisk: Text
    ) : async Bool {
        let currentTime = Time.now();
        
        // Generate audit hash for transparency
        let auditData = id # status # Nat.toText(validationScore) # Int.toText(currentTime);
        let auditHash = ?auditData; // In production, use proper hash function
        
        let invoice : InvoiceRecord = {
            id = id;
            vendor_name = vendor_name;
            tax_id = tax_id;
            amount = amount;
            date = date;
            status = status;
            explanation = explanation;
            timestamp = currentTime;
            blockchain_hash = blockchain_hash;
            riskScore = riskScore;
            validationScore = validationScore;
            fraudRisk = fraudRisk;
            processedAt = currentTime;
            auditHash = auditHash;
        };
        
        invoices.put(id, invoice);
        
        // Log the storage action
        ignore await logAudit(id, "STORED", "Invoice stored with validation score: " # Nat.toText(validationScore));
        
        Debug.print("Invoice stored: " # id # " with status: " # status);
        true
    };

    // Get invoice by ID - required for chat agent queries
    public query func getInvoice(id: Text) : async ?InvoiceRecord {
        invoices.get(id)
    };

    // Get all invoices - required for chat agent statistics
    public query func getAllInvoices() : async [InvoiceRecord] {
        Iter.toArray(invoices.vals())
    };

    // Get invoices by status
    public query func getInvoicesByStatus(status: Text) : async [InvoiceRecord] {
        let filtered = Iter.filter(invoices.vals(), func (record: InvoiceRecord) : Bool {
            record.status == status
        });
        Iter.toArray(filtered)
    };

    // Update invoice status
    public func updateInvoiceStatus(id: Text, newStatus: Text, explanation: Text) : async Bool {
        switch (invoices.get(id)) {
            case (?existing) {
                let updated : InvoiceRecord = {
                    id = existing.id;
                    vendor_name = existing.vendor_name;
                    tax_id = existing.tax_id;
                    amount = existing.amount;
                    date = existing.date;
                    status = newStatus;
                    explanation = explanation;
                    timestamp = existing.timestamp;
                    blockchain_hash = existing.blockchain_hash;
                    riskScore = existing.riskScore;
                    validationScore = existing.validationScore;
                    fraudRisk = existing.fraudRisk;
                    processedAt = existing.processedAt;
                    auditHash = existing.auditHash;
                };
                invoices.put(id, updated);
                ignore await logAudit(id, "STATUS_UPDATED", "Status changed to: " # newStatus);
                true
            };
            case null { false };
        }
    };

    // Log audit action
    public func logAudit(invoice_id: Text, action: Text, details: Text) : async Text {
        auditCounter += 1;
        let logId = "AUDIT_" # Nat.toText(auditCounter);
        
        let auditLog : AuditLog = {
            invoice_id = invoice_id;
            action = action;
            timestamp = Time.now();
            details = details;
        };
        
        auditLogs.put(logId, auditLog);
        Debug.print("Audit logged: " # logId # " for invoice: " # invoice_id);
        logId
    };

    // Get audit logs for specific invoice
    public query func getAuditLogs(invoice_id: Text) : async [AuditLog] {
        let filtered = Iter.filter(auditLogs.vals(), func (log: AuditLog) : Bool {
            log.invoice_id == invoice_id
        });
        Iter.toArray(filtered)
    };

    // Get all audit logs
    public query func getAllAuditLogs() : async [AuditLog] {
        Iter.toArray(auditLogs.vals())
    };

    // Get invoice count - simple method for testing
    public query func getInvoiceCount() : async Nat {
        invoices.size()
    };

    // Get invoice statistics
    public query func getStats() : async {approved: Nat; rejected: Nat; total: Nat} {
        let all = Iter.toArray(invoices.vals());
        var approved = 0;
        var rejected = 0;
        
        for (invoice in all.vals()) {
            if (invoice.status == "approved") {
                approved += 1;
            } else if (invoice.status == "rejected") {
                rejected += 1;
            };
        };
        
        {approved = approved; rejected = rejected; total = all.size()}
    };

    // Health check
    public query func health() : async Text {
        "InvoiceLogger Canister is running - Invoices: " # Nat.toText(invoices.size()) # ", Audit Logs: " # Nat.toText(auditLogs.size())
    };

    // System functions for upgrades
    system func preupgrade() {
        invoiceEntries := Iter.toArray(invoices.entries());
        auditEntries := Iter.toArray(auditLogs.entries());
    };

    system func postupgrade() {
        invoiceEntries := [];
        auditEntries := [];
    };
}

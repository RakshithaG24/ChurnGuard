
import { useCallback, useEffect, useState } from "react";
import {
  Search,
  Users,
  RefreshCw,
  ServerCrash,
  UserX,
  X,
} from "lucide-react";
import api from "../services/api";

interface Customer {
  customer_id: string;
  tenure: number;
  contract: string;
  monthly_charges: number;
  churn_probability: number;
  churn_percentage: number;
  risk_level: "High" | "Medium" | "Low";
}

interface CustomerResponse {
  total: number;
  limit: number;
  offset: number;
  customers: Customer[];
}

const Customers = () => {
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [search, setSearch] = useState("");
  const [risk, setRisk] = useState("All");
  const [page, setPage] = useState(0);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const limit = 10;
  const totalPages = Math.ceil(total / limit);

  const fetchCustomers = useCallback(async () => {
    setLoading(true);
    setError("");

    try {
      const response = await api.get<CustomerResponse>("/customers", {
        params: {
          search,
          risk,
          limit,
          offset: page * limit,
        },
      });

      const data = response.data;

      if (
        !data ||
        !Array.isArray(data.customers) ||
        !Number.isFinite(data.total)
      ) {
        throw new Error("Invalid customer response");
      }

      setCustomers(data.customers);
      setTotal(data.total);
    } catch {
      setCustomers([]);
      setTotal(0);
      setError(
        "Unable to load customer records. Please check whether the ChurnGuard API is running."
      );
    } finally {
      setLoading(false);
    }
  }, [search, risk, page]);

  useEffect(() => {
    fetchCustomers();
  }, [fetchCustomers]);

  const changeSearch = (value: string) => {
    setSearch(value);
    setPage(0);
  };

  const changeRisk = (value: string) => {
    setRisk(value);
    setPage(0);
  };

  const clearFilters = () => {
    setSearch("");
    setRisk("All");
    setPage(0);
  };

  return (
    <main className="dashboard customers-page">
      <header className="dashboard-header">
        <div>
          <h1>Customer Management</h1>
          <p>Search customers and monitor their predicted churn risk.</p>
        </div>

        <button
          className="refresh-button"
          onClick={fetchCustomers}
          disabled={loading}
        >
          <RefreshCw size={16} className={loading ? "spin" : ""} />
          {loading ? "Refreshing..." : "Refresh"}
        </button>
      </header>

      <section className="customer-summary">
        <div className="customer-summary-icon">
          <Users size={25} />
        </div>
        <div>
          <span>Total matching customers</span>
          <h2>{loading ? "—" : total.toLocaleString()}</h2>
        </div>
      </section>

      <section className="customer-table-card">
        <div className="customer-toolbar">
          <div className="customer-search">
            <Search size={18} />
            <input
              type="text"
              placeholder="Search customer ID or contract..."
              value={search}
              onChange={(e) => changeSearch(e.target.value)}
            />
            {search && (
              <button
                className="clear-search"
                onClick={() => changeSearch("")}
                title="Clear search"
                aria-label="Clear search"
              >
                <X size={16} />
              </button>
            )}
          </div>

          <select
            className="risk-filter"
            value={risk}
            onChange={(e) => changeRisk(e.target.value)}
            aria-label="Filter by risk level"
          >
            <option value="All">All Risk Levels</option>
            <option value="High">High Risk</option>
            <option value="Medium">Medium Risk</option>
            <option value="Low">Low Risk</option>
          </select>
        </div>

        {error ? (
          <div className="customer-state error-state">
            <ServerCrash size={38} />
            <h3>Unable to load customers</h3>
            <p>{error}</p>
            <button className="retry-button" onClick={fetchCustomers}>
              <RefreshCw size={16} />
              Retry
            </button>
          </div>
        ) : loading ? (
          <div className="customer-loading">
            <div className="customer-loading-heading">
              Loading customer records...
            </div>

            {Array.from({ length: 6 }).map((_, index) => (
              <div className="customer-skeleton-row" key={index}>
                <div className="skeleton" />
                <div className="skeleton" />
                <div className="skeleton" />
                <div className="skeleton" />
              </div>
            ))}
          </div>
        ) : customers.length === 0 ? (
          <div className="customer-state empty-state">
            <UserX size={40} />
            <h3>No matching customers found</h3>
            <p>
              {search || risk !== "All"
                ? "Try changing your search term or risk filter."
                : "There are currently no customer records to display."}
            </p>

            {(search || risk !== "All") && (
              <button className="retry-button" onClick={clearFilters}>
                <X size={16} />
                Clear filters
              </button>
            )}
          </div>
        ) : (
          <div className="table-scroll">
            <table className="customer-table">
              <thead>
                <tr>
                  <th>Customer ID</th>
                  <th>Tenure</th>
                  <th>Contract</th>
                  <th>Monthly Charges</th>
                  <th>Churn Probability</th>
                  <th>Risk Level</th>
                </tr>
              </thead>

              <tbody>
                {customers.map((customer) => (
                  <tr key={customer.customer_id}>
                    <td className="customer-id">{customer.customer_id}</td>
                    <td>{customer.tenure} months</td>
                    <td>{customer.contract}</td>
                    <td>₹{customer.monthly_charges.toFixed(2)}</td>
                    <td>
                      <div className="probability-cell">
                        <span>{customer.churn_percentage.toFixed(2)}%</span>
                        <div className="probability-track">
                          <div
                            className={`probability-fill ${customer.risk_level.toLowerCase()}`}
                            style={{
                              width: `${Math.max(
                                0,
                                Math.min(100, customer.churn_percentage)
                              )}%`,
                            }}
                          />
                        </div>
                      </div>
                    </td>
                    <td>
                      <span
                        className={`risk-badge ${customer.risk_level.toLowerCase()}`}
                      >
                        {customer.risk_level}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {!error && !loading && customers.length > 0 && (
          <div className="customer-pagination">
            <span>
              Showing {page * limit + 1}–
              {Math.min((page + 1) * limit, total)} of {total} customers
            </span>

            <div>
              <button
                disabled={page === 0}
                onClick={() => setPage((current) => Math.max(0, current - 1))}
              >
                Previous
              </button>

              <span>
                Page {page + 1} of {totalPages}
              </span>

              <button
                disabled={page + 1 >= totalPages}
                onClick={() =>
                  setPage((current) =>
                    Math.min(totalPages - 1, current + 1)
                  )
                }
              >
                Next
              </button>
            </div>
          </div>
        )}
      </section>
    </main>
  );
};

export default Customers;

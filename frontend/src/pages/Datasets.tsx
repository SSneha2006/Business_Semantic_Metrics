
import { useEffect, useState, type ChangeEvent } from "react";
import {
  Upload,
  FileSpreadsheet,
  Trash2,
  Eye,
  X,
} from "lucide-react";
import axios from "axios";

interface Dataset {
  id: number;
  name: string;
  rows: number;
  columns: number;
  size: string;
  preview: string[][];
}

const API_URL = "http://127.0.0.1:8000/api";

export default function Datasets() {
  const [datasets, setDatasets] = useState<Dataset[]>([]);
  const [selected, setSelected] = useState<Dataset | null>(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  // Load datasets from the backend
  const fetchDatasets = async () => {
    try {
      const response = await axios.get(
        `${API_URL}/datasets/?workspace_id=1`
      );

      const savedDatasets: Dataset[] = response.data.map(
        (item: any) => ({
          id: item.id,
          name: item.filename,
          rows: item.rows,
          columns: item.columns,
          size: (item.file_size / 1024).toFixed(1) + " KB",
          preview: [],
        })
      );

      setDatasets(savedDatasets);
    } catch {
      setError("Unable to load datasets. Check whether the backend is running.");
    }
  };

  useEffect(() => {
    fetchDatasets();
  }, []);

  // Upload dataset to backend
  const uploadFile = async (
    event: ChangeEvent<HTMLInputElement>
  ) => {
    const file = event.target.files?.[0];
    if (!file) return;

    setError("");

    const extension = file.name.split(".").pop()?.toLowerCase();

    if (!["csv", "xlsx", "xls"].includes(extension || "")) {
      setError("Please upload a CSV or Excel file.");
      event.target.value = "";
      return;
    }

    const formData = new FormData();
    formData.append("file", file);

    setLoading(true);

    try {
      await axios.post(
        `${API_URL}/datasets/upload?workspace_id=1&user_id=1`,
        formData
      );

      await fetchDatasets();
    } catch (err: any) {
      setError(
        err.response?.data?.detail || "Unable to upload the dataset."
      );
    } finally {
      setLoading(false);
      event.target.value = "";
    }
  };

  // Preview dataset from backend
  const previewDataset = async (dataset: Dataset) => {
    setError("");

    try {
      const response = await axios.get(
        `${API_URL}/datasets/${dataset.id}/preview?workspace_id=1`
      );

      const previewData = [
        response.data.columns.map(String),
        ...response.data.preview.map((row: unknown[]) =>
          row.map(String)
        ),
      ];

      setSelected({
        ...dataset,
        preview: previewData,
      });
    } catch (err: any) {
      setError(
        err.response?.data?.detail || "Unable to preview this dataset."
      );
    }
  };

  // Delete dataset from backend
  const deleteDataset = async (id: number) => {
    setError("");

    try {
      await axios.delete(
        `${API_URL}/datasets/${id}?workspace_id=1`
      );

      setDatasets(previous =>
        previous.filter(item => item.id !== id)
      );

      if (selected?.id === id) {
        setSelected(null);
      }
    } catch (err: any) {
      setError(
        err.response?.data?.detail || "Unable to delete this dataset."
      );
    }
  };

  return (
    <div className="dashboard-page">
      <div className="welcome-section">
        <div>
          <h1>Dataset Management</h1>
          <p>Upload, preview and manage your business datasets.</p>
        </div>
      </div>

      <div className="upload-card">
        <div className="upload-icon">
          <Upload size={30} />
        </div>

        <h3>Upload Your Dataset</h3>
        <p>Choose a CSV or Excel file to get started.</p>

        <label className="primary-button upload-button">
          <Upload size={17} />
          {loading ? "Uploading..." : "Choose File"}

          <input
            type="file"
            accept=".csv,.xlsx,.xls"
            onChange={uploadFile}
            hidden
            disabled={loading}
          />
        </label>

        <small>Supported formats: CSV, XLSX, XLS</small>

        {error && <p className="upload-error">{error}</p>}
      </div>

      <div className="dataset-table-card">
        <div className="dataset-heading">
          <div>
            <h3>Uploaded Datasets</h3>
            <p>{datasets.length} datasets available</p>
          </div>
        </div>

        <div className="table-scroll">
          <table className="dataset-table">
            <thead>
              <tr>
                <th>Dataset Name</th>
                <th>Rows</th>
                <th>Columns</th>
                <th>File Size</th>
                <th>Actions</th>
              </tr>
            </thead>

            <tbody>
              {datasets.map(dataset => (
                <tr key={dataset.id}>
                  <td>
                    <div className="file-name">
                      <FileSpreadsheet size={19} />
                      {dataset.name}
                    </div>
                  </td>

                  <td>{dataset.rows}</td>
                  <td>{dataset.columns}</td>
                  <td>{dataset.size}</td>

                  <td>
                    <button
                      className="table-action"
                      onClick={() => previewDataset(dataset)}
                      title="Preview"
                    >
                      <Eye size={17} />
                    </button>

                    <button
                      className="table-action delete-action"
                      onClick={() => deleteDataset(dataset.id)}
                      title="Delete"
                    >
                      <Trash2 size={17} />
                    </button>
                  </td>
                </tr>
              ))}

              {datasets.length === 0 && (
                <tr>
                  <td colSpan={5} className="empty-state">
                    No datasets uploaded yet. Choose a file to get started.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      {selected && (
        <div className="preview-overlay">
          <div className="preview-modal">
            <div className="preview-heading">
              <div>
                <h3>Dataset Preview</h3>
                <p>{selected.name}</p>
              </div>

              <button
                className="table-action"
                onClick={() => setSelected(null)}
              >
                <X size={20} />
              </button>
            </div>

            <div className="table-scroll">
              <table className="dataset-table">
                <tbody>
                  {selected.preview.map((row, index) => (
                    <tr key={index}>
                      {row.map((cell, cellIndex) =>
                        index === 0 ? (
                          <th key={cellIndex}>{cell}</th>
                        ) : (
                          <td key={cellIndex}>{cell}</td>
                        )
                      )}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            <p className="preview-note">
              Showing the first {selected.preview.length} rows.
            </p>
          </div>
        </div>
      )}
    </div>
  );
}

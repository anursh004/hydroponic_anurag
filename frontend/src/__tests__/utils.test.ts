import {
  cn,
  formatNumber,
  formatCurrency,
  getSensorUnit,
  getSeverityColor,
  getStatusColor,
} from "@/lib/utils";

describe("cn utility", () => {
  it("merges class names", () => {
    expect(cn("text-red-500", "bg-blue-500")).toContain("text-red-500");
    expect(cn("text-red-500", "bg-blue-500")).toContain("bg-blue-500");
  });

  it("handles conditional classes", () => {
    expect(cn("base", false && "hidden")).toBe("base");
    expect(cn("base", true && "visible")).toBe("base visible");
  });

  it("merges tailwind conflicts", () => {
    const result = cn("px-4", "px-6");
    expect(result).toBe("px-6");
  });
});

describe("formatNumber", () => {
  it("formats with default decimals", () => {
    expect(formatNumber(3.14159)).toBe("3.14");
  });

  it("formats with custom decimals", () => {
    expect(formatNumber(3.14159, 3)).toBe("3.142");
  });

  it("formats integer", () => {
    expect(formatNumber(42)).toBe("42.00");
  });
});

describe("formatCurrency", () => {
  it("formats USD currency", () => {
    const result = formatCurrency(1234.56);
    expect(result).toContain("1,234.56");
  });

  it("handles zero", () => {
    const result = formatCurrency(0);
    expect(result).toContain("0.00");
  });
});

describe("getSensorUnit", () => {
  it("returns correct units", () => {
    expect(getSensorUnit("temperature")).toBe("\u00B0C");
    expect(getSensorUnit("humidity")).toBe("%");
    expect(getSensorUnit("co2")).toBe("ppm");
    expect(getSensorUnit("ec")).toBe("mS/cm");
    expect(getSensorUnit("ph")).toBe("");
  });

  it("returns empty for unknown type", () => {
    expect(getSensorUnit("unknown")).toBe("");
  });
});

describe("getSeverityColor", () => {
  it("returns correct colors", () => {
    expect(getSeverityColor("critical")).toContain("red");
    expect(getSeverityColor("warning")).toContain("yellow");
    expect(getSeverityColor("info")).toContain("blue");
  });
});

describe("getStatusColor", () => {
  it("returns correct status colors", () => {
    expect(getStatusColor("active")).toContain("red");
    expect(getStatusColor("resolved")).toContain("green");
    expect(getStatusColor("pending")).toContain("yellow");
    expect(getStatusColor("completed")).toContain("green");
    expect(getStatusColor("in_progress")).toContain("blue");
  });
});

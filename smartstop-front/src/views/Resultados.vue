<script setup>
import { ref, computed, onMounted, onUnmounted } from "vue";
import { useRouter } from "vue-router";
import {
  Plane,
  Search,
  ArrowRightLeft,
  Bell,
  AlertTriangle,
  MapPin,
  User,
  Calendar,
  ChevronDown,
  ShieldCheck,
  Sparkles,
} from "lucide-vue-next";

const router = useRouter();
const isSearching = ref(true);
const rawResults = ref([]);

const searchPayload = ref({
  origin: "",
  destination: "",
  departure_date: "",
  return_date: "",
  passengers: 1,
  cabin_class: "Económica",
  trip_type: "ida-vuelta",
});

const activeCabinClass = ref("Económica");

const allAirports = ref([]);
const originResults = ref([]);
const destResults = ref([]);
const showOriginDropdown = ref(false);
const showDestDropdown = ref(false);

const filterStops = ref([]);
const filterMaxPrice = ref(5000);
const filterAirlines = ref([]);
const sortBy = ref("mejor");

const selectedCurrency = ref("CLP");
const exchangeRates = { EUR: 1, USD: 1.08, CLP: 1000 };

const showDatePicker = ref(false);
const hoverDate = ref(null);
const currentMonthOffset = ref(0);
const todayObj = new Date();
const todayStr = `${todayObj.getFullYear()}-${String(todayObj.getMonth() + 1).padStart(2, "0")}-${String(todayObj.getDate()).padStart(2, "0")}`;

const getMonthData = (offset) => {
  const d = new Date(todayObj.getFullYear(), todayObj.getMonth() + offset, 1);
  const monthName = new Intl.DateTimeFormat("es-CL", {
    month: "long",
    year: "numeric",
  }).format(d);
  const days = [];
  const firstDay = (d.getDay() + 6) % 7;
  for (let i = 0; i < firstDay; i++) days.push({ empty: true });
  const lastDay = new Date(d.getFullYear(), d.getMonth() + 1, 0).getDate();
  for (let i = 1; i <= lastDay; i++) {
    const dateStr = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(i).padStart(2, "0")}`;
    days.push({ empty: false, day: i, dateStr });
  }
  return { title: monthName, days };
};

const month1 = computed(() => getMonthData(currentMonthOffset.value));
const month2 = computed(() => getMonthData(currentMonthOffset.value + 1));
const nextMonth = () => currentMonthOffset.value++;
const prevMonth = () => currentMonthOffset.value--;

const formatDisplayDate = (dateStr) => {
  if (!dateStr) return "";
  return new Intl.DateTimeFormat("es-CL", {
    weekday: "short",
    day: "numeric",
    month: "short",
  }).format(new Date(dateStr + "T12:00:00"));
};

const isPastDate = (dateStr) => dateStr < todayStr;
const isDateInRange = (dateStr) => {
  if (searchPayload.value.trip_type === "ida") return false;
  if (!searchPayload.value.departure_date) return false;
  const end = searchPayload.value.return_date || hoverDate.value;
  if (!end || isPastDate(dateStr)) return false;
  return dateStr > searchPayload.value.departure_date && dateStr < end;
};
const isDateSelected = (dateStr) =>
  dateStr === searchPayload.value.departure_date ||
  dateStr === searchPayload.value.return_date;

const handleDateClick = (dateStr) => {
  if (isPastDate(dateStr)) return;
  if (searchPayload.value.trip_type === "ida") {
    searchPayload.value.departure_date = dateStr;
    searchPayload.value.return_date = null;
    showDatePicker.value = false;
  } else {
    if (
      !searchPayload.value.departure_date ||
      (searchPayload.value.departure_date && searchPayload.value.return_date)
    ) {
      searchPayload.value.departure_date = dateStr;
      searchPayload.value.return_date = null;
    } else {
      if (dateStr < searchPayload.value.departure_date)
        searchPayload.value.departure_date = dateStr;
      else {
        searchPayload.value.return_date = dateStr;
        showDatePicker.value = false;
      }
    }
  }
};

const closeCalendarOutside = (e) => {
  const cal = document.getElementById("kayak-calendar");
  const trigger = document.getElementById("calendar-trigger");
  if (
    showDatePicker.value &&
    cal &&
    !cal.contains(e.target) &&
    trigger &&
    !trigger.contains(e.target)
  )
    showDatePicker.value = false;
};

onMounted(async () => {
  window.addEventListener("click", closeCalendarOutside);
  try {
    const res = await apiClient("/vuelos/aeropuertos");
    allAirports.value = res;
  } catch (e) {
    console.error(e);
  }

  const data =
    sessionStorage.getItem("smartstop_search_params") ||
    sessionStorage.getItem("smartstop_search");
  if (!data) {
    router.push("/");
    return;
  }

  const parsed = JSON.parse(data);
  searchPayload.value = {
    ...parsed,
    origin: parsed.origen_iata || parsed.origin,
    destination: parsed.destino_iata || parsed.destination,
    departure_date: parsed.fecha_salida || parsed.departure_date,
    return_date: parsed.fecha_regreso || parsed.return_date,
  };

  activeCabinClass.value = searchPayload.value.cabin_class;
  fetchRealResults(parsed);
});

onUnmounted(() => window.removeEventListener("click", closeCalendarOutside));

const normalizeText = (text) =>
  text
    ? text
        .normalize("NFD")
        .replace(/[\u0300-\u036f]/g, "")
        .toLowerCase()
    : "";
const filterAirports = (query) => {
  if (query.length < 2) return [];
  const q = normalizeText(query);
  return allAirports.value.filter(
    (a) =>
      (a.nombre && normalizeText(a.nombre).includes(q)) ||
      (a.codigo_iata && normalizeText(a.codigo_iata).includes(q)) ||
      (a.pais && normalizeText(a.pais).includes(q)),
  );
};

const buscarOrigen = (q) => {
  originResults.value = filterAirports(q);
};
const buscarDestino = (q) => {
  destResults.value = filterAirports(q);
};
const selectOrigin = (apt) => {
  searchPayload.value.origin = `${apt.codigo_iata} - ${apt.nombre}`;
  showOriginDropdown.value = false;
};
const selectDest = (apt) => {
  searchPayload.value.destination = `${apt.codigo_iata} - ${apt.nombre}`;
  showDestDropdown.value = false;
};
function hideOriginDropdown() {
  setTimeout(() => {
    showOriginDropdown.value = false;
  }, 200);
}
function hideDestDropdown() {
  setTimeout(() => {
    showDestDropdown.value = false;
  }, 200);
}

const swapDestinations = () => {
  const temp = searchPayload.value.origin;
  searchPayload.value.origin = searchPayload.value.destination;
  searchPayload.value.destination = temp;
};

const fetchRealResults = async (payload) => {
  isSearching.value = true;
  try {
    const backendPayload = {
      trip_type: payload.trip_type || payload.tripType || "ida-vuelta",
      origen_iata: (payload.origen_iata || payload.origin)
        .split("-")[0]
        .trim()
        .toUpperCase(),
      destino_iata: (payload.destino_iata || payload.destination)
        .split("-")[0]
        .trim()
        .toUpperCase(),
      fecha_salida: payload.fecha_salida || payload.departure_date,
      fecha_regreso: payload.fecha_regreso || payload.return_date || null,
      passengers: parseInt(payload.passengers) || 1,
      cabin_class: payload.cabin_class || payload.cabinClass || "Económica",
      cabin_bag: payload.cabin_bag || 0,
      checked_bag: payload.checked_bag || 0,
      equipaje_alto: payload.equipaje_alto || 0,
      equipaje_ancho: payload.equipaje_ancho || 0,
      equipaje_largo: payload.equipaje_largo || 0,
      equipaje_peso: payload.equipaje_peso || 0,
    };

    const resultados = await apiClient("/vuelos/buscar", {
      method: "POST",
      body: JSON.stringify(backendPayload),
    });

    if (resultados && Array.isArray(resultados)) {
      rawResults.value = resultados;
      if (rawResults.value.length > 0) {
        filterMaxPrice.value = Math.max(
          ...rawResults.value.map((r) => r.precio_vuelo_clp),
        );
      }
    } else {
      rawResults.value = [];
    }
  } catch (error) {
    console.error(error);
    rawResults.value = [];
  } finally {
    isSearching.value = false;
  }
};

const executeNewSearch = () => {
  activeCabinClass.value = searchPayload.value.cabin_class;
  sessionStorage.setItem(
    "smartstop_search_params",
    JSON.stringify(searchPayload.value),
  );
  fetchRealResults(searchPayload.value);
};

const availableAirlines = computed(() =>
  Array.from(new Set(rawResults.value.map((r) => r.aerolinea_owner))),
);

const filteredAndSortedResults = computed(() => {
  let result = rawResults.value.filter((flight) => {
    if (flight.precio_vuelo_clp > filterMaxPrice.value) return false;
    if (filterStops.value.length > 0) {
      const anyDirect = flight.trayectos.some((t) => t.es_directo);
      const anyOneStop = flight.trayectos.some(
        (t) => !t.es_directo && t.info_escalas === "1 escala(s)",
      );
      const matchDirecto = filterStops.value.includes("directo") && anyDirect;
      const match1 = filterStops.value.includes("1") && anyOneStop;
      if (!matchDirecto && !match1 && !filterStops.value.includes("2"))
        return false;
    }
    if (
      filterAirlines.value.length > 0 &&
      !filterAirlines.value.includes(flight.aerolinea_owner)
    )
      return false;
    return true;
  });

  if (sortBy.value === "barato")
    result.sort((a, b) => a.precio_vuelo_clp - b.precio_vuelo_clp);
  else if (sortBy.value === "duracion")
    result.sort((a, b) =>
      a.duracion_total_formato.localeCompare(b.duracion_total_formato),
    );
  else if (sortBy.value === "mejor")
    result.sort((a, b) => a.precio_vuelo_clp - b.precio_vuelo_clp);

  return result;
});

const formatPrice = (basePriceEur) => {
  const rate = exchangeRates[selectedCurrency.value];
  const converted = basePriceEur * rate;
  if (selectedCurrency.value === "CLP")
    return new Intl.NumberFormat("es-CL", {
      style: "currency",
      currency: "CLP",
      maximumFractionDigits: 0,
    }).format(converted);
  else if (selectedCurrency.value === "EUR")
    return new Intl.NumberFormat("es-ES", {
      style: "currency",
      currency: "EUR",
      maximumFractionDigits: 0,
    }).format(converted);
  else
    return new Intl.NumberFormat("en-US", {
      style: "currency",
      currency: "USD",
      maximumFractionDigits: 0,
    }).format(converted);
};
</script>

<template>
  <div class="min-h-screen bg-slate-50 pb-12 font-sans text-slate-800">
    <!-- BARRA SUPERIOR -->
    <div class="bg-white border-b border-slate-200 sticky top-0 z-40 shadow-sm">
      <div
        class="max-w-[1400px] mx-auto px-4 py-3 flex flex-wrap lg:flex-nowrap items-center gap-3"
      >
        <select
          v-model="searchPayload.trip_type"
          @change="
            searchPayload.trip_type === 'ida'
              ? (searchPayload.return_date = null)
              : ''
          "
          class="border border-slate-300 rounded-lg px-3 py-2 bg-slate-50 text-sm font-semibold outline-none hover:bg-slate-100"
        >
          <option value="ida-vuelta">Ida y vuelta</option>
          <option value="ida">Solo ida</option>
          <option value="multidestino">Stopover Automático ✨</option>
        </select>

        <div class="flex-1 flex flex-wrap md:flex-nowrap items-center gap-2">
          <div
            class="flex items-center border border-slate-300 rounded-lg bg-white focus-within:ring-2 ring-[#f95d3c] w-full md:w-auto flex-1 relative"
          >
            <div class="w-full relative">
              <input
                v-model="searchPayload.origin"
                @input="buscarOrigen(searchPayload.origin)"
                @focus="showOriginDropdown = true"
                @blur="hideOriginDropdown"
                class="w-full bg-transparent text-sm font-bold outline-none uppercase py-2 px-3 truncate"
                placeholder="Origen"
              />
              <div
                v-if="showOriginDropdown && originResults.length > 0"
                class="absolute top-full left-0 mt-1 w-[250px] bg-white border border-slate-200 shadow-xl rounded-xl z-50 overflow-hidden"
              >
                <div
                  v-for="apt in originResults"
                  :key="apt.codigo_iata"
                  @click="selectOrigin(apt)"
                  class="px-4 py-2 hover:bg-blue-50 cursor-pointer flex justify-between items-center border-b border-slate-50"
                >
                  <span
                    class="font-bold text-slate-700 text-xs truncate mr-2"
                    >{{ apt.nombre }}</span
                  ><span
                    class="text-[10px] font-black bg-slate-100 px-1.5 py-0.5 rounded"
                    >{{ apt.codigo_iata }}</span
                  >
                </div>
              </div>
            </div>
            <button
              @click="swapDestinations"
              class="mx-1 text-slate-400 hover:text-[#f95d3c] p-1 rounded-full hover:bg-slate-100 transition"
            >
              <ArrowRightLeft class="w-4 h-4" />
            </button>
            <div class="w-full relative">
              <input
                v-model="searchPayload.destination"
                @input="buscarDestino(searchPayload.destination)"
                @focus="showDestDropdown = true"
                @blur="hideDestDropdown"
                class="w-full bg-transparent text-sm font-bold outline-none uppercase py-2 px-3 text-right truncate"
                placeholder="Destino"
              />
              <div
                v-if="showDestDropdown && destResults.length > 0"
                class="absolute top-full right-0 mt-1 w-[250px] bg-white border border-slate-200 shadow-xl rounded-xl z-50 overflow-hidden text-left"
              >
                <div
                  v-for="apt in destResults"
                  :key="apt.codigo_iata"
                  @click="selectDest(apt)"
                  class="px-4 py-2 hover:bg-blue-50 cursor-pointer flex justify-between items-center border-b border-slate-50"
                >
                  <span
                    class="font-bold text-slate-700 text-xs truncate mr-2"
                    >{{ apt.nombre }}</span
                  ><span
                    class="text-[10px] font-black bg-slate-100 px-1.5 py-0.5 rounded"
                    >{{ apt.codigo_iata }}</span
                  >
                </div>
              </div>
            </div>
          </div>

          <div class="relative w-full md:w-auto flex-1">
            <div
              id="calendar-trigger"
              @click.stop="showDatePicker = !showDatePicker"
              class="flex items-center border border-slate-300 rounded-lg px-3 py-2 bg-white cursor-pointer hover:bg-slate-50 transition h-[38px]"
            >
              <Calendar class="w-4 h-4 text-slate-400 mr-2 shrink-0" />
              <div
                class="flex items-center w-full"
                :class="{
                  'divide-x divide-slate-200':
                    searchPayload.trip_type !== 'ida',
                }"
              >
                <div
                  class="w-full text-sm font-bold text-slate-800 text-center truncate px-1"
                  :class="{ 'text-slate-400': !searchPayload.departure_date }"
                >
                  {{
                    searchPayload.departure_date
                      ? formatDisplayDate(searchPayload.departure_date)
                      : "Fecha Ida"
                  }}
                </div>
                <div
                  v-if="searchPayload.trip_type !== 'ida'"
                  class="w-full text-sm font-bold text-slate-800 text-center truncate px-1"
                  :class="{ 'text-slate-400': !searchPayload.return_date }"
                >
                  {{
                    searchPayload.return_date
                      ? formatDisplayDate(searchPayload.return_date)
                      : "Vuelta"
                  }}
                </div>
              </div>
            </div>

            <div
              v-if="showDatePicker"
              id="kayak-calendar"
              class="absolute top-full right-0 mt-2 bg-white rounded-2xl shadow-2xl border border-slate-200 p-6 z-50 w-[320px] md:w-[680px]"
            >
              <div class="flex justify-between items-center mb-6">
                <button
                  @click.stop="prevMonth"
                  class="p-2 hover:bg-slate-100 rounded-full"
                >
                  <ChevronDown class="w-5 h-5 rotate-90 text-slate-600" />
                </button>
                <div class="flex gap-16 md:gap-32 w-full justify-center">
                  <h3
                    class="font-extrabold text-slate-800 capitalize w-32 text-center"
                  >
                    {{ month1.title }}
                  </h3>
                  <h3
                    class="font-extrabold text-slate-800 capitalize w-32 text-center hidden md:block"
                  >
                    {{ month2.title }}
                  </h3>
                </div>
                <button
                  @click.stop="nextMonth"
                  class="p-2 hover:bg-slate-100 rounded-full"
                >
                  <ChevronDown class="w-5 h-5 -rotate-90 text-slate-600" />
                </button>
              </div>
              <div
                class="grid grid-cols-1 md:grid-cols-2 gap-8 text-center text-sm font-semibold text-slate-800"
              >
                <div>
                  <div
                    class="grid grid-cols-7 gap-y-2 mb-2 text-[10px] font-black text-slate-400 uppercase tracking-wider"
                  >
                    <span>Lu</span><span>Ma</span><span>Mi</span><span>Ju</span
                    ><span>Vi</span><span>Sa</span><span>Do</span>
                  </div>
                  <div class="grid grid-cols-7 gap-y-1 gap-x-0">
                    <div
                      v-for="(day, idx) in month1.days"
                      :key="'m1' + idx"
                      @mouseenter="
                        !isPastDate(day?.dateStr) && (hoverDate = day?.dateStr)
                      "
                      class="relative h-10 w-full flex items-center justify-center"
                    >
                      <template v-if="!day.empty">
                        <div
                          v-if="isDateInRange(day.dateStr)"
                          class="absolute inset-0 bg-blue-50/80 -z-10"
                        ></div>
                        <div
                          v-if="
                            day.dateStr === searchPayload.departure_date &&
                            searchPayload.return_date
                          "
                          class="absolute inset-y-0 right-0 w-1/2 bg-blue-50/80 -z-10"
                        ></div>
                        <div
                          v-if="
                            day.dateStr === searchPayload.return_date &&
                            searchPayload.departure_date
                          "
                          class="absolute inset-y-0 left-0 w-1/2 bg-blue-50/80 -z-10"
                        ></div>
                        <button
                          @click.stop="handleDateClick(day.dateStr)"
                          :disabled="isPastDate(day.dateStr)"
                          :class="[
                            'w-full h-full flex items-center justify-center transition-colors',
                            isPastDate(day.dateStr)
                              ? 'text-slate-300 cursor-not-allowed z-10'
                              : isDateSelected(day.dateStr)
                                ? 'bg-[#03254c] text-white rounded-md font-bold z-10 shadow-sm'
                                : 'hover:border hover:border-slate-300 rounded-md z-10 text-slate-700',
                          ]"
                        >
                          {{ day.day }}
                        </button>
                      </template>
                    </div>
                  </div>
                </div>
                <div class="hidden md:block">
                  <div
                    class="grid grid-cols-7 gap-y-2 mb-2 text-[10px] font-black text-slate-400 uppercase tracking-wider"
                  >
                    <span>Lu</span><span>Ma</span><span>Mi</span><span>Ju</span
                    ><span>Vi</span><span>Sa</span><span>Do</span>
                  </div>
                  <div class="grid grid-cols-7 gap-y-1 gap-x-0">
                    <div
                      v-for="(day, idx) in month2.days"
                      :key="'m2' + idx"
                      @mouseenter="
                        !isPastDate(day?.dateStr) && (hoverDate = day?.dateStr)
                      "
                      class="relative h-10 w-full flex items-center justify-center"
                    >
                      <template v-if="!day.empty">
                        <div
                          v-if="isDateInRange(day.dateStr)"
                          class="absolute inset-0 bg-blue-50/80 -z-10"
                        ></div>
                        <div
                          v-if="
                            day.dateStr === searchPayload.departure_date &&
                            searchPayload.return_date
                          "
                          class="absolute inset-y-0 right-0 w-1/2 bg-blue-50/80 -z-10"
                        ></div>
                        <div
                          v-if="
                            day.dateStr === searchPayload.return_date &&
                            searchPayload.departure_date
                          "
                          class="absolute inset-y-0 left-0 w-1/2 bg-blue-50/80 -z-10"
                        ></div>
                        <button
                          @click.stop="handleDateClick(day.dateStr)"
                          :disabled="isPastDate(day.dateStr)"
                          :class="[
                            'w-full h-full flex items-center justify-center transition-colors',
                            isPastDate(day.dateStr)
                              ? 'text-slate-300 cursor-not-allowed z-10'
                              : isDateSelected(day.dateStr)
                                ? 'bg-[#03254c] text-white rounded-md font-bold z-10 shadow-sm'
                                : 'hover:border hover:border-slate-300 rounded-md z-10 text-slate-700',
                          ]"
                        >
                          {{ day.day }}
                        </button>
                      </template>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="flex items-center gap-2 w-full lg:w-auto">
          <div
            class="flex items-center border border-slate-300 rounded-lg px-3 py-2 bg-white flex-1 lg:w-28"
          >
            <User class="w-4 h-4 text-slate-400 mr-2 shrink-0" />
            <input
              type="number"
              min="1"
              max="9"
              v-model="searchPayload.passengers"
              class="w-8 bg-transparent text-sm font-bold outline-none"
            />
          </div>
          <select
            v-model="searchPayload.cabin_class"
            class="border border-slate-300 rounded-lg px-2 py-2 bg-white text-sm font-semibold outline-none flex-1 lg:w-32"
          >
            <option>Económica</option>
            <option>Premium</option>
            <option>Business</option>
          </select>
          <button
            @click="executeNewSearch"
            class="bg-[#f95d3c] hover:bg-[#e04f30] text-white px-6 py-2 rounded-lg font-bold text-sm shadow-md transition-all active:scale-95 h-[38px]"
          >
            Buscar
          </button>
        </div>
      </div>
    </div>

    <!-- MAIN GRID -->
    <div class="max-w-[1400px] mx-auto px-4 py-6">
      <div class="flex justify-end mb-4">
        <div
          class="flex items-center bg-white rounded-lg border border-slate-200 shadow-sm p-1"
        >
          <span class="text-xs font-bold text-slate-500 px-3">Moneda:</span>
          <select
            v-model="selectedCurrency"
            class="text-sm font-black text-[#03254c] bg-transparent outline-none cursor-pointer pr-2"
          >
            <option value="CLP">CLP ($)</option>
            <option value="EUR">EUR (€)</option>
            <option value="USD">USD ($)</option>
          </select>
        </div>
      </div>

      <div class="grid grid-cols-1 lg:grid-cols-12 gap-6">
        <aside class="lg:col-span-3 hidden lg:block space-y-5">
          <div
            class="bg-white rounded-xl border border-slate-200 p-4 shadow-sm flex items-center justify-between"
          >
            <div>
              <h3 class="font-bold text-sm flex items-center gap-2">
                Recibe alertas <Bell class="w-4 h-4 text-[#f95d3c]" />
              </h3>
            </div>
            <div
              class="w-10 h-5 bg-slate-200 rounded-full relative cursor-pointer"
            >
              <div
                class="w-4 h-4 bg-white rounded-full absolute left-0.5 top-0.5 shadow-sm"
              ></div>
            </div>
          </div>
          <div
            class="bg-white rounded-xl border border-slate-200 p-4 shadow-sm"
            v-if="rawResults.length > 0"
          >
            <div class="flex items-center justify-between mb-3">
              <h3 class="font-bold text-sm">Precio máximo</h3>
              <span class="text-xs font-bold text-[#f95d3c]">{{
                formatPrice(filterMaxPrice)
              }}</span>
            </div>
            <input
              type="range"
              :min="Math.min(...rawResults.map((r) => r.precio_vuelo_clp))"
              :max="Math.max(...rawResults.map((r) => r.precio_vuelo_clp)) + 50"
              v-model="filterMaxPrice"
              class="w-full accent-[#03254c]"
            />
          </div>
        </aside>

        <main class="lg:col-span-9 space-y-4">
          <div
            v-if="isSearching"
            class="bg-white p-20 rounded-xl border border-slate-200 shadow-sm flex flex-col items-center justify-center h-[400px]"
          >
            <div
              class="w-10 h-10 border-4 border-slate-100 border-t-[#03254c] rounded-full animate-spin mb-4"
            ></div>
            <h4 class="font-bold text-lg">Buscando los mejores vuelos...</h4>
          </div>

          <template v-else>
            <div
              v-if="rawResults.length > 0"
              class="bg-white rounded-xl border border-slate-200 shadow-sm flex overflow-hidden"
            >
              <button
                @click="sortBy = 'mejor'"
                :class="
                  sortBy === 'mejor'
                    ? 'border-b-4 border-[#03254c] bg-slate-50'
                    : 'hover:bg-slate-50'
                "
                class="flex-1 py-3 px-4 text-left border-r border-slate-200 transition-colors"
              >
                <span class="block text-sm font-bold text-slate-800"
                  >El mejor</span
                >
              </button>
              <button
                @click="sortBy = 'barato'"
                :class="
                  sortBy === 'barato'
                    ? 'border-b-4 border-[#03254c] bg-slate-50'
                    : 'hover:bg-slate-50'
                "
                class="flex-1 py-3 px-4 text-left border-r border-slate-200 transition-colors"
              >
                <span class="block text-sm font-bold text-slate-800"
                  >El más barato</span
                >
              </button>
            </div>

            <!-- TARJETAS DE VUELO CON LÓGICA STOPOVER -->
            <div
              v-for="flight in filteredAndSortedResults"
              :key="flight.offer_id"
              class="bg-white rounded-xl border border-slate-200 shadow-sm hover:shadow-md transition relative overflow-hidden flex flex-col md:flex-row items-stretch"
            >
              <div class="flex-1 flex flex-col">
                <!-- BANNER DE EQUIPAJE / STOPOVER -->
                <div
                  v-if="flight.es_stopover"
                  class="bg-emerald-500 border-b border-emerald-600 px-4 py-2 flex items-center justify-between"
                >
                  <div class="flex items-center gap-2 text-white">
                    <Sparkles class="w-4 h-4" />
                    <span class="text-xs font-extrabold uppercase tracking-wide"
                      >Stopover Automático Encontrado</span
                    >
                  </div>
                  <span
                    class="text-xs font-black bg-white text-emerald-800 px-2 py-0.5 rounded-full"
                    >{{ flight.stopover_hours }}h en
                    {{ flight.stopover_city }}</span
                  >
                </div>
                <div
                  v-else-if="!flight.cumple_equipaje"
                  class="bg-red-50 border-b border-red-100 px-4 py-2 flex items-center gap-2"
                >
                  <AlertTriangle class="w-4 h-4 text-red-500" />
                  <span class="text-xs font-bold text-red-800"
                    >Multa estimada en puerta:
                    {{ formatPrice(flight.multa_estimada_clp) }}</span
                  >
                </div>
                <div
                  v-else
                  class="bg-slate-50 border-b border-slate-100 px-4 py-2 flex items-center gap-2"
                >
                  <ShieldCheck class="w-4 h-4 text-slate-500" />
                  <span class="text-xs font-bold text-slate-600"
                    >Equipaje IATA verificado.</span
                  >
                </div>

                <div class="p-5 flex flex-col gap-6">
                  <div
                    v-for="(trayecto, idx) in flight.trayectos"
                    :key="idx"
                    class="flex flex-col md:flex-row items-start md:items-center gap-4 w-full"
                  >
                    <div class="w-full md:w-1/4 flex items-center gap-3">
                      <div
                        class="w-8 h-8 rounded bg-[#03254c] text-white flex items-center justify-center text-xs font-black shrink-0"
                      >
                        {{ trayecto.aerolinea }}
                      </div>
                      <div>
                        <p class="text-sm font-bold leading-tight truncate">
                          {{ trayecto.aerolinea_nombre }}
                        </p>
                        <p class="text-[10px] text-slate-400 truncate">
                          {{ trayecto.tipo_avion }}
                        </p>
                      </div>
                    </div>
                    <div class="w-full md:w-1/4 flex flex-col">
                      <p class="text-lg font-black text-slate-800">
                        {{ trayecto.hora_salida }}
                        <span class="text-slate-400 mx-1">-</span>
                        {{ trayecto.hora_llegada }}
                      </p>
                      <p
                        class="text-xs text-slate-500 font-bold uppercase tracking-wide"
                      >
                        {{ trayecto.origen }} <span class="mx-0.5">-</span>
                        {{ trayecto.destino }}
                      </p>
                    </div>
                    <div class="w-full md:w-1/4 flex flex-col">
                      <p
                        class="text-sm font-bold"
                        :class="
                          trayecto.es_directo
                            ? 'text-emerald-600'
                            : 'text-slate-700'
                        "
                      >
                        {{ trayecto.info_escalas }}
                      </p>
                    </div>
                    <div
                      class="w-full md:w-1/4 flex flex-col md:items-end text-left md:text-right"
                    >
                      <p class="text-sm font-bold text-slate-800">
                        {{ trayecto.duracion_formato }}
                      </p>
                    </div>
                  </div>
                </div>
              </div>

              <!-- PRECIO -->
              <div
                class="w-full md:w-56 border-t md:border-t-0 md:border-l border-slate-200 p-6 flex flex-col justify-center items-center shrink-0 bg-slate-50"
              >
                <p
                  class="text-[10px] text-slate-500 font-semibold mb-1 uppercase tracking-wider text-center"
                >
                  Clase {{ activeCabinClass }}
                </p>
                <p
                  class="text-3xl font-black text-[#03254c] leading-none mb-4 text-center"
                >
                  {{ formatPrice(flight.precio_vuelo_clp) }}
                </p>
                <button
                  class="w-full bg-[#f95d3c] hover:bg-[#e04f30] text-white rounded-lg py-3 font-bold text-sm transition-colors shadow-sm active:scale-95"
                >
                  Seleccionar
                </button>
              </div>
            </div>
          </template>
        </main>
      </div>
    </div>
  </div>
</template>

<style scoped>
.custom-scrollbar::-webkit-scrollbar {
  width: 4px;
}
.custom-scrollbar::-webkit-scrollbar-track {
  background: #f1f5f9;
}
.custom-scrollbar::-webkit-scrollbar-thumb {
  background: #cbd5e1;
  border-radius: 4px;
}
</style>
